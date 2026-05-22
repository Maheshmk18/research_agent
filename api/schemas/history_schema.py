from datetime import datetime
from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    topic: str
    status: str
    created_at: datetime
    model_config = {"populate_by_name": True}


class HistoryDetail(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    topic: str
    final_report: str
    status: str
    created_at: datetime
    verified_at: datetime
    model_config = {"populate_by_name": True}
