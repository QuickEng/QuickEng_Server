"""
Google Gemini API를 이용한 요약 및 분석 서비스
"""
import google.generativeai as genai
from app.core.config import settings

# Gemini 설정
genai.configure(api_key=settings.gemini_api_key)

async def summarize_transcript(transcript: str) -> dict:
    """
    자막을 요약하고 핵심 포인트를 추출합니다.
    
    Args:
        transcript: 추출된 자막 텍스트
    
    Returns:
        {
            "summary": "요약 텍스트",
            "key_points": ["포인트1", "포인트2", ...]
        }
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
다음 유튜브 비디오 자막을 분석해 주세요.

자막:
{transcript}

다음을 제공해주세요:
1. 전체 내용의 요약 (3-5문장)
2. 핵심 포인트 5개 (각각 한 문장)

응답 형식:
<summary>
요약 내용
</summary>

<key_points>
- 포인트 1
- 포인트 2
- 포인트 3
- 포인트 4
- 포인트 5
</key_points>
"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        # 응답 파싱
        summary = extract_section(result_text, "summary")
        key_points = extract_key_points(result_text)
        
        return {
            "summary": summary,
            "key_points": key_points
        }
    
    except Exception as e:
        raise Exception(f"Failed to summarize transcript: {str(e)}")

def extract_section(text: str, section: str) -> str:
    """XML 스타일 섹션 추출"""
    import re
    pattern = f"<{section}>(.*?)</{section}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_key_points(text: str) -> list[str]:
    """핵심 포인트 추출"""
    import re
    key_points_section = extract_section(text, "key_points")
    points = re.findall(r'-\s*(.+)', key_points_section)
    return [point.strip() for point in points]
