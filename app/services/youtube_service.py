"""
=============================================================================
[YouTube Transcript Service]
설명: 유튜브 영상의 자막(스크립트)을 가져오는 역할을 합니다.
핵심: 'youtube-transcript-api' 라이브러리를 사용하며,
      서버가 멈추지 않도록 비동기(Async) 방식으로 동작합니다.
=============================================================================
"""

import re
import asyncio
import logging
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

# 커스텀 에러 임포트
from app.core.exceptions import (
    NoTranscriptException, 
    TranscriptsDisabledException, 
    YouTubeUnknownException,
    InvalidLinkException
)

# 로거 설정
logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> str:
    """
    [기능 1] 유튜브 링크에서 '영상 ID'만 쏙 뽑아냅니다.
    예: https://youtu.be/abc12345 -> abc12345
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', 
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    # ID 추출 실패 시 커스텀 에러 발생
    raise InvalidLinkException()



def _fetch_transcript_sync(video_id: str):
    """
    [동기 함수] 실제 자막을 다운로드합니다.
    ★ 중요: 영어 학습 앱이므로 '영어 자막'이 없으면 에러 처리합니다.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # [수정 포인트]
        # 사용자가 요청한 언어(targetLang)와 상관없이, 
        # 원본 소스는 무조건 '영어(English)'여야만 함.
        # 한국어 자막만 있는 영상이라면 여기서 NoTranscriptFound 에러가 터짐 -> 아래 catch 블록으로 이동
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        
        return transcript.fetch()

    except TranscriptsDisabled:
        # 자막 기능이 꺼진 경우
        raise TranscriptsDisabledException()

    except NoTranscriptFound:
        # [핵심 의도 반영]
        # 영어가 없으면 (한국어가 있더라도) '자막 없음'으로 처리
        raise NoTranscriptException()


async def get_transcript_list(video_url: str, language: str = "en") -> list[dict]:
    """
    [메인 함수] 
    외부(Router)에서 호출하는 비동기 함수입니다.
    (language 파라미터는 추후 확장성을 위해 남겨두지만, 현재 로직에서는 영어만 강제합니다)
    """
    try:
        # 1. URL에서 ID 추출
        video_id = extract_video_id(video_url)
        
        # 2. 비동기 스레드로 자막 다운로드 실행
        # _fetch_transcript_sync 함수가 '영어'만 찾으므로, 실패 시 에러가 올라옴
        transcript_data = await asyncio.to_thread(_fetch_transcript_sync, video_id)
        
        return transcript_data


    
    # --- [에러 처리 구간] ---
    
    # CASE 1: 이미 우리가 의도한대로 변환된 커스텀 에러들
    except (InvalidLinkException, NoTranscriptException, TranscriptsDisabledException) as e:
        # 로그에는 경고 수준으로 남기고 그대로 던짐 -> Video Router가 받아서 400 응답
        logger.warning(f"예상된 에러 발생 ({type(e).__name__}): {str(e)}")
        raise e
        
    # CASE 2: 정말 예상치 못한 시스템 에러
    except Exception as e:
        logger.error(f"YouTube 추출 치명적 오류: {str(e)}")
        raise YouTubeUnknownException()
