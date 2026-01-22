# app/routers/video.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, ScriptItem, WordItem

# 서비스 로직 임포트
from app.services.youtube_service import get_transcript_list 
from app.services.gemini_service import extract_vocabulary

# 커스텀 에러 임포트 (InvalidLinkException 포함 확인!)
from app.core.exceptions import (
    NoTranscriptException,
    TranscriptsDisabledException,
    YouTubeUnknownException,
    AIParseException,
    AIUnknownException,
    InvalidLinkException  # <--- [필수] 이거 없으면 에러 못 잡습니다!
)

router = APIRouter(prefix="/v1/video", tags=["video"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_video(request: AnalyzeRequest):
    """
    유튜브 비디오 분석 API
    1. 자막 추출 (YouTube)
    2. 단어장 생성 (Gemini)
    """
    try:
        # 1. 자막 추출 (YouTube Service)
        # 반환값: [{'text': 'Hello', 'start': 0.0, 'duration': 1.5}, ...]
        transcript_data = await get_transcript_list(str(request.video_url), request.language)
        
        # 2. 핵심 표현 추출 (Gemini Service)
        # 반환값: [{'id': '...', 'expression': '...', 'meaningKr': '...', 'contextTag': '...'}, ...]
        vocabulary_data = await extract_vocabulary(transcript_data)
        
        # 3. Pydantic 모델로 변환 (데이터 검증)
        script_items = [ScriptItem(**item) for item in transcript_data]
        word_items = [WordItem(**item) for item in vocabulary_data]
        
        # 4. 최종 응답 생성
        return AnalyzeResponse(
            video_url=request.video_url,
            script=script_items,
            words=word_items
        )

    # =========================================================
    # [에러 핸들링] API 명세서 규격 준수 ({code, message})
    # =========================================================
    
    # 1. 링크가 잘못됨 (400)
    except InvalidLinkException:
        return JSONResponse(
            status_code=400,
            content={"code": "INVALID_LINK", "message": "유효하지 않은 유튜브 링크입니다."}
        )

    # 2. 자막 없음 (400)
    except NoTranscriptException:
        return JSONResponse(
            status_code=400,
            content={"code": "NO_TRANSCRIPT", "message": "이 영상은 영어 자막을 지원하지 않습니다."}
        )

    # 3. 자막 기능 꺼짐 (400)
    except TranscriptsDisabledException:
        return JSONResponse(
            status_code=400,
            content={"code": "TRANSCRIPT_DISABLED", "message": "이 영상은 자막이 비활성화되어 있습니다."}
        )
    
    # 4. AI 파싱 실패 (500)
    except AIParseException:
        return JSONResponse(
            status_code=500,
            content={"code": "AI_PARSE_ERROR", "message": "AI 분석 결과 처리에 실패했습니다."}
        )
    
    # 5. 기타 서버 에러 (500)
    except (YouTubeUnknownException, AIUnknownException) as e:
        return JSONResponse(
            status_code=500,
            content={"code": "SERVER_ERROR", "message": "서버 내부 로직 오류가 발생했습니다."}
        )
        
    except Exception as e:
        # 예상치 못한 시스템 에러
        return JSONResponse(
            status_code=500,
            content={"code": "UNKNOWN_ERROR", "message": f"알 수 없는 오류: {str(e)}"}
        )
