"""
YouTube 자막 추출 서비스
"""
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    """
    유튜브 URL에서 Video ID 추출
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be/)([^&\n?#]+)',
        r'youtube\.com\/embed/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid YouTube URL")

async def get_transcript(video_url: str, language: str = "en") -> str:
    """
    유튜브 비디오의 자막을 추출합니다.
    
    Args:
        video_url: 유튜브 비디오 URL
        language: 자막 언어 코드 (기본값: en)
    
    Returns:
        추출된 자막 텍스트
    """
    try:
        video_id = extract_video_id(video_url)
        
        # 자막 추출
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        # 자막 텍스트 합치기
        transcript = " ".join([item["text"] for item in transcript_list])
        
        return transcript
    
    except Exception as e:
        raise Exception(f"Failed to extract transcript: {str(e)}")
