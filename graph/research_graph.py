from datetime import datetime
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from langsmith import traceable
from agents.fact_checker import run_fact_checker
from agents.search_agent import run_search
from agents.supervisor import run_supervisor
from agents.writer_agent import run_writer
from db.mongodb import save_agent_log, save_plan, save_raw_data, save_report
from db.pinecone_db import embed_text, save_report_vector
from utils.logger import get_logger


logger = get_logger("research_graph")

#state  
class ResearchState(TypedDict, total=False):
    topic: str
    plan: str
    query: str
    sources: list
    draft_report: str
    final_report: str
    word_count: int
    pinecone_id: str
    report_id: str


#nodes
def plan_node(state: ResearchState):
    topic = state["topic"]
    logger.info("Plan step started for topic='%s'", topic)
    save_agent_log(topic, "supervisor_agent", "started", input_text=topic)
    plan = run_supervisor(topic)
    save_plan(topic, plan, "completed")
    save_agent_log(
        topic,
        "supervisor_agent",
        "completed",
        input_text=topic,
        output_text=plan,
    )
    logger.info("Plan step completed for topic='%s'", topic)
    return {"plan": plan}


def search_node(state: ResearchState):
    topic = state["topic"]
    logger.info("Search step started for topic='%s'", topic)
    save_agent_log(topic, "search_agent", "started", input_text=topic)
    search_result = run_search(topic)
    query = search_result["query"]
    sources = search_result["sources"]
    save_raw_data(topic, query, sources)
    save_agent_log(
        topic,
        "search_agent",
        "completed",
        input_text=query,
        output_text=f"Collected {len(sources)} sources",
    )
    logger.info("Search step completed for topic='%s' sources=%s", topic, len(sources))
    return {"query": query, "sources": sources}


def writer_node(state: ResearchState):
    topic = state["topic"]
    plan = state["plan"]
    sources = state["sources"]
    logger.info("Writer step started for topic='%s'", topic)
    save_agent_log(topic, "writer_agent", "started", input_text=topic)
    draft_report = run_writer(topic, plan, sources)
    save_agent_log(
        topic,
        "writer_agent",
        "completed",
        input_text=topic,
        output_text=draft_report,
    )
    logger.info("Writer step completed for topic='%s'", topic)
    return {"draft_report": draft_report}


def fact_checker_node(state: ResearchState):
    topic = state["topic"]
    draft_report = state["draft_report"]
    sources = state["sources"]
    logger.info("Fact check step started for topic='%s'", topic)
    save_agent_log(topic, "fact_checker", "started", input_text=topic)
    final_report = run_fact_checker(draft_report, sources)
    word_count = len(final_report.split())
    pinecone_id = topic.lower().replace(" ", "_")
    report_id = save_report(
        topic=topic,
        draft_report=draft_report,
        final_report=final_report,
        status="verified",
        pinecone_id=pinecone_id,
        word_count=word_count,
    )
    vector = embed_text(final_report, input_type="passage")
    save_report_vector(
        vector_id=pinecone_id,
        values=vector,
        topic=topic,
        mongo_id=str(report_id),
        status="verified",
        verified="yes",
        word_count=word_count,
        created_at=datetime.utcnow().isoformat(),
    )
    save_agent_log(
        topic,
        "fact_checker",
        "completed",
        input_text=draft_report,
        output_text=final_report,
    )
    logger.info("Fact check step completed for topic='%s' report_id='%s'", topic, str(report_id))
    return {
        "final_report": final_report,
        "word_count": word_count,
        "pinecone_id": pinecone_id,
        "report_id": str(report_id),
    }


graph_builder = StateGraph(ResearchState)

# Edge
graph_builder.add_node("plan_step", plan_node)
graph_builder.add_node("search_step", search_node)
graph_builder.add_node("write_step", writer_node)
graph_builder.add_node("fact_check_step", fact_checker_node)
graph_builder.add_edge(START, "plan_step")
graph_builder.add_edge("plan_step", "search_step")
graph_builder.add_edge("search_step", "write_step")
graph_builder.add_edge("write_step", "fact_check_step")
graph_builder.add_edge("fact_check_step", END)

#compile graph
research_graph = graph_builder.compile()

@traceable(name="research_graph.run")
def run_research_graph(topic: str):
    logger.info("Research graph invoked for topic='%s'", topic)
    return research_graph.invoke({"topic": topic})
