from pydantic import BaseModel
from typing import Optional

class VideoAnalyzeRequest(BaseModel):
    video_url: str
    language: Optional[str] = "en"

class VideoAnalyzeResponse(BaseModel):
    video_url: str
    transcript: str
    summary: str
    key_points: list[str]

class TranscriptResponse(BaseModel):
    transcript: str

class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
