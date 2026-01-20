from fastapi import APIRouter, HTTPException
from app.models.schemas import VideoAnalyzeRequest, VideoAnalyzeResponse
from app.services.youtube_service import get_transcript
from app.services.gemini_service import summarize_transcript

router = APIRouter(prefix="/api/video", tags=["video"])

@router.post("/analyze", response_model=VideoAnalyzeResponse)
async def analyze_video(request: VideoAnalyzeRequest):
    """
    유튜브 비디오 분석
    - 자막 추출
    - Gemini로 요약 및 핵심 포인트 추출
    """
    try:
        # 자막 추출
        transcript = await get_transcript(request.video_url)
        
        # Gemini 요약
        summary_result = await summarize_transcript(transcript)
        
        return VideoAnalyzeResponse(
            video_url=request.video_url,
            transcript=transcript,
            summary=summary_result["summary"],
            key_points=summary_result["key_points"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transcript")
async def get_video_transcript(video_url: str):
    """유튜브 비디오에서 자막 추출"""
    try:
        transcript = await get_transcript(video_url)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
