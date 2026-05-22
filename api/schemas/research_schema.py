from datetime import datetime
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str


class ReportSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class PlanDocument(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    topic: str
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "topic": "AI in Healthcare",
                "plan": "Step 1: Search sources. Step 2: Write report.",
                "status": "completed",
            }
        },
    }


class SourceItem(BaseModel):
    url: str
    content: str


class RawDataDocument(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    topic: str
    query: str
    sources: list[SourceItem]
    total_sources: int
    searched_at: datetime
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "topic": "AI in Healthcare",
                "query": "AI healthcare 2024",
                "sources": [
                    {
                        "url": "https://example.com",
                        "content": "Sample source content",
                    }
                ],
                "total_sources": 5,
            }
        },
    }


class ReportDocument(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    topic: str
    draft_report: str
    final_report: str
    status: str
    pinecone_id: str
    word_count: int
    created_at: datetime
    verified_at: datetime
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "topic": "AI in Healthcare",
                "final_report": "AI is transforming diagnosis and care delivery.",
                "status": "verified",
                "pinecone_id": "ai_in_healthcare",
            }
        },
    }


class AgentLogDocument(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    topic: str
    agent_name: str
    status: str
    input: str
    output: str
    time_taken: str
    error: str
    timestamp: datetime

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "agent_name": "search_agent",
                "status": "completed",
                "time_taken": "2.3s",
            }
        },
    }


class PineconeMetadata(BaseModel):
    topic: str
    mongo_id: str
    status: str
    verified: str
    word_count: int
    created_at: str


class PineconeVector(BaseModel):
    id: str
    values: list[float]
    metadata: PineconeMetadata


class ResearchResponse(BaseModel):
    topic: str
    status: str
    message: str
