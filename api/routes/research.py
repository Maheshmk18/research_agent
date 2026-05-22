from fastapi import APIRouter, HTTPException
from langsmith import traceable
from api.schemas import ReportSearchRequest, ResearchRequest, ResearchResponse
from db.mongodb import get_report_by_mongo_id, save_agent_log
from db.pinecone_db import embed_text, search_report_vectors
from graph.research_graph import run_research_graph
from utils.logger import get_logger


router = APIRouter(prefix="/research", tags=["research"])
logger = get_logger("research_api")


@router.post("/create", response_model=ResearchResponse)

@traceable(name="research_api.create_research")  # langsmith traceable decorator 

def create_research(request: ResearchRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        logger.info("Research request received for topic='%s'", topic)
        result = run_research_graph(topic)
        logger.info(
            "Research workflow completed for topic='%s' report_id='%s'",
            topic,
            result["report_id"],
        )

        return ResearchResponse(
            topic=topic,
            status="verified",
            message=f"Research saved successfully with id {result['report_id']}",
        )
    except Exception as exc:
        logger.exception("Research workflow failed for topic='%s'", topic)
        save_agent_log(topic, "research_workflow", "failed", input_text=topic, error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/search")
@traceable(name="research_api.search_research_reports")
def search_research_reports(request: ReportSearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        logger.info(
            "Report search request received for query='%s' top_k=%s",
            query,
            request.top_k,
        )
        vector = embed_text(query, input_type="query")
        result = search_report_vectors(vector, top_k=request.top_k)
        matches = []

        for match in result.get("matches", []):
            metadata = match.get("metadata", {})
            report = None

            mongo_id = metadata.get("mongo_id")
            if mongo_id:
                try:
                    report = get_report_by_mongo_id(mongo_id)
                except Exception:
                    report = None

            if report:
                report = {
                    "_id": str(report["_id"]),
                    "topic": report.get("topic"),
                    "final_report": report.get("final_report"),
                    "status": report.get("status"),
                    "pinecone_id": report.get("pinecone_id"),
                    "word_count": report.get("word_count"),
                    "created_at": report.get("created_at"),
                    "verified_at": report.get("verified_at"),
                }

            matches.append(
                {
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "metadata": metadata,
                    "report": report,
                }
            )

        logger.info(
            "Report search completed for query='%s' matches=%s",
            query,
            len(matches),
        )
        return {"query": query, "matches": matches}
    except Exception as exc:
        logger.exception("Report search failed for query='%s'", query)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
