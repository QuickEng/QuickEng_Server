"""
=============================================================================
[YouTube Transcript Service]
설명: 유튜브 영상의 자막(스크립트)을 가져오는 역할을 합니다.
핵심: 'youtube-transcript-api' 라이브러리를 사용하며,
      서버가 멈추지 않도록 비동기(Async) 방식으로 동작합니다.
=============================================================================
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import asyncio
import logging
import json
from app.core.exceptions import (
    NoTranscriptException, 
    TranscriptsDisabledException, 
    YouTubeUnknownException,
)

# 로거 설정
logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> str:
    """
    [기능 1] 유튜브 링크에서 '영상 ID'만 쏙 뽑아냅니다.
    예: https://youtu.be/abc12345 -> abc12345
    """
    # 정규식 패턴: 일반 영상(v=), 단축 링크(/), 임베드, 쇼츠 등 모든 주소 대응
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', 
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1) # 찾은 ID 반환
            
    raise ValueError("올바르지 않은 유튜브 주소입니다.")


# app/services/youtube_service.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
# ★ 방금 만든 에러 클래스 가져오기
from app.core.exceptions import NoTranscriptException, InvalidLinkException 

# ... (기타 import 및 extract_video_id 함수 생략) ...

def _fetch_transcript_sync(video_id: str, language: str):
    """
    [동기 함수] 실제 자막을 다운로드합니다.
    영어가 없으면 절대 다른 언어를 가져오지 않고 에러를 냅니다.
    """
    try:
        # 1. 자막 목록 가져오기
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 2. 자막 검색 (우선순위: 요청언어 -> 미국영어 -> 영국영어)
        # 만약 여기서 못 찾으면 라이브러리가 자동으로 'NoTranscriptFound' 에러를 냅니다.
        transcript = transcript_list.find_transcript([language, 'en', 'en-US', 'en-GB'])
        
        # 3. 찾았으면 다운로드
        return transcript.fetch()

    except (NoTranscriptFound, TranscriptsDisabled):
        # [수정됨]
        # 예전에는 여기서 transcript_list[0]을 했지만,
        # 이제는 "영어가 없으면 그냥 끝내라"는 뜻으로 바로 에러를 던집니다.
        raise NoTranscriptException()


async def get_transcript_list(video_url: str, language: str = "en") -> list[dict]:
    """
    [메인 함수] 
    외부(API)에서 호출하는 함수입니다. 자막을 리스트 형태로 가져옵니다.
    
    Args:
        video_url: 유튜브 링크
        language: 선호하는 언어 코드 (기본값: 'en')
        
    Returns:
        list[dict]: 자막 한 줄씩 담긴 리스트
    """
    try:
        # 1. URL에서 ID 추출
        video_id = extract_video_id(video_url)
        
        # 2. [핵심] 비동기 처리 (Non-blocking)
        # 자막을 다운로드하는 동안 서버가 멈추지 않고 다른 요청을 받을 수 있게,
        # 별도의 스레드(일꾼)에게 작업을 맡깁니다.
        transcript_data = await asyncio.to_thread(_fetch_transcript_sync, video_id, language)
        
        return transcript_data
    
# --- [에러 처리 구간] ---
    
    except TranscriptsDisabled:
        # 유튜버가 자막을 끈 경우 -> 표준 에러 발생
        logger.warning(f"자막 비활성화 영상 요청됨: {video_url}")
        raise TranscriptsDisabledException()
        
    except NoTranscriptFound:
        # (아까 만든) 자막이 없는 경우 -> 표준 에러 발생
        logger.warning(f"자막 없음 (언어: {language}): {video_url}")
        raise NoTranscriptException()
        
    except Exception as e:
        # 그 외 모든 에러 (네트워크, 알 수 없는 오류)
        # print 대신 logger로 기록!
        logger.error(f"YouTube 추출 치명적 오류: {str(e)}")
        
        # 빈 리스트([]) 대신 확실하게 에러를 던짐!
        # 그래야 앱이 "재시도 버튼"을 띄울 수 있음
        raise YouTubeUnknownException()
