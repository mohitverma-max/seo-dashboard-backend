from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class RunMonitorRequest(BaseModel):
    url: str = Field(..., description="Target website URL to audit")
    keywords: Optional[list[str]] = Field(default=[], description="Keywords to track")
    depth: Optional[int] = Field(default=1, ge=1, le=5, description="Crawl depth")

    model_config = {"json_schema_extra": {"example": {
        "url": "https://example.com",
        "keywords": ["seo dashboard", "rank tracker"],
        "depth": 1,
    }}}


class OptimizeRequest(BaseModel):
    content: str = Field(..., min_length=10, description="HTML or plain text content to optimize")
    target_keyword: str = Field(..., description="Primary keyword to optimize for")
    task_id: Optional[str] = Field(default=None, description="Link to an existing monitor task")

    model_config = {"json_schema_extra": {"example": {
        "content": "<p>Welcome to our site...</p>",
        "target_keyword": "seo tools",
    }}}


class FeedbackRequest(BaseModel):
    task_id: str = Field(..., description="Task ID returned by /run-monitor or /optimize")
    feedback: str = Field(..., min_length=1, description="Human feedback to apply")

    model_config = {"json_schema_extra": {"example": {
        "task_id": "task-abc123",
        "feedback": "Focus more on mobile SEO recommendations.",
    }}}


class ApprovalRequest(BaseModel):
    task_id: str = Field(..., description="Task ID to approve or reject")
    note: Optional[str] = Field(default=None, description="Optional reviewer note")
