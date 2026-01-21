"""
Google Gemini API를 이용한 요약 및 분석 서비스
"""
import google.generativeai as genai
from app.core.config import settings
import json
import uuid  # [1] 내장 라이브러리 추가 (고유 ID 생성용)

# =============================================================================
# Gemini API 초기 설정
# =============================================================================
genai.configure(api_key=settings.gemini_api_key)

async def extract_vocabulary(transcript_list: list[dict]) -> list[dict]:
    """
    자막 텍스트를 분석하여 학습용 주요 표현, 한국어 뜻, 문맥 태그를 추출하고
    각 항목에 고유 ID(UUID)를 부여합니다.
    
    Args:
        transcript_list: [{'text': '...', 'start': ...}, ...] 형태의 자막 리스트
    
    Returns:
        [
            {
                "id": "550e8400-e29b...",      # 서버에서 생성한 고유 ID
                "expression": "영어 표현",
                "meaningKr": "한국어 뜻",
                "contextTag": "문맥 태그"
            },
            ...
        ]
    """
    try:
        # ---------------------------------------------------------
        # 1. 텍스트 전처리 (Preprocessing)
        # ---------------------------------------------------------
        # 자막 리스트에서 텍스트만 추출하여 하나의 긴 문자열로 병합
        full_text = " ".join([item["text"] for item in transcript_list])
        
        # ---------------------------------------------------------
        # 2. 모델 선택 (Model Initialization)
        # ---------------------------------------------------------
        model = genai.GenerativeModel("gemini-pro")
        
        # ---------------------------------------------------------
        # 3. 프롬프트 구성 (Prompt Engineering)
        # ---------------------------------------------------------
        # - 표현 3개 추출
        # - JSON 포맷 엄수
        prompt = f"""
        Analyze the following English transcript and extract 3 key expressions for learning English.
        
        For each expression, provide:
        1. "expression": The exact English phrase used in the text.
        2. "meaningKr": The Korean meaning suitable for the context.
        3. "contextTag": A short, uppercase tag describing the mood or situation (e.g., ROMANTIC, ANGER, BUSINESS, GREETING, SLANG).

        Transcript:
        {full_text}

        Return strictly a JSON list. Do not use Markdown code blocks.
        The Output must follow this JSON format:
        [
            {{
                "expression": "expression here",
                "meaningKr": "korean meaning here",
                "contextTag": "TAG_NAME"
            }}
        ]
        """
        
        # ---------------------------------------------------------
        # 4. API 요청 및 응답 (Request & Response)
        # ---------------------------------------------------------
        response = model.generate_content(prompt)
        result_text = response.text
        
        # ---------------------------------------------------------
        # 5. 결과 파싱 및 후처리 (Parsing & Post-processing)
        # ---------------------------------------------------------
        # 마크다운 코드 블록(```json) 제거
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
            
        # 문자열 -> 파이썬 리스트 변환
        vocabulary_data = json.loads(result_text)

        # =========================================================
        # [2] ID 생성 로직 (Unique ID Injection)
        # =========================================================
        # 파이썬이 직접 '전 세계에서 유일한 ID(UUID)'를 발급해서 붙여줍니다.
        # DB 충돌 방지 및 안드로이드 프론트엔드 식별용
        for item in vocabulary_data:
            item["id"] = str(uuid.uuid4())
        
        return vocabulary_data
    
    # ---------------------------------------------------------
    # 6. 예외 처리 (Error Handling)
    # ---------------------------------------------------------
    # 상황: AI가 JSON 형식이 아닌 그냥 줄글(예: "안녕하세요, 여기 단어입니다...")을 보냈을 때 json.loads에서 에러가 납니다.
    # 프로그램이 멈추지 않게 "형식이 틀렸네요"라고 로그를 남기고, **빈 리스트([])**를 줘서 다음 단계가 문제없이 넘어가게 합니다.
    except json.JSONDecodeError:
        print("Gemini Response Parse Error: JSON 형식이 아닙니다.")
        return []
    # 상황: 인터넷이 끊기거나, API 키가 틀리는 등 예상치 못한 다른 모든 에러가 발생했을 때입니다.
    # 에러 내용을 출력해서 개발자가 알 수 있게 하고, 마찬가지로 빈 리스트를 반환하여 프로그램 셧다운을 막습니다.
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return []