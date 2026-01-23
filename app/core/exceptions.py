# app/core/exceptions.py

# 가장 먼저 부모 클래스(뼈대)를 정의합니다.
class BusinessException(Exception):
    # [수정] detail, code, status_code 외에 message도 받을 수 있게 수정
    def __init__(self, detail: str = None, code: str = "ERROR", status_code: int = 400, message: str = None):
        # detail이 있으면 쓰고, 없으면 message를 쓰고, 둘 다 없으면 기본 문구 사용
        self.detail = detail or message or "알 수 없는 오류가 발생했습니다."
        self.code = code
        self.status_code = status_code
# ... (기존 BusinessException, NoTranscriptException 등 아래에 추가) ...

# 1. AI 응답이 JSON 형식이 아닐 때 (파싱 에러)
class AIParseException(BusinessException):
    def __init__(self):
        super().__init__(
            code="AI_PARSE_ERROR",
            message="AI 분석 결과가 올바르지 않습니다. 다시 시도해주세요."
        )

# 2. 그 외 알 수 없는 에러 (서버 내부 오류)
class AIUnknownException(BusinessException):
    def __init__(self, debug_message: str = ""):
        # [추가] 여기도 동일하게 추가
        self.debug_message = debug_message

        # debug_message는 로그용으로 받아두되, 클라이언트에게는 안전한 메시지만 보냄
        super().__init__(
            code="UNKNOWN_ERROR",
            message="알 수 없는 오류가 발생했습니다."
        )



# 3. "자막을 못 찾았을 때" 사용할 에러

class NoTranscriptException(BusinessException):
    def __init__(self):
        super().__init__(
            code="NO_TRANSCRIPT",
            message="요청하신 언어(영어)의 자막을 찾을 수 없습니다."
        )





# 4. 유튜버가 자막 기능을 꺼놓은 경우
class TranscriptsDisabledException(BusinessException):
    def __init__(self):
        super().__init__(
            code="TRANSCRIPTS_DISABLED",
            message="이 영상은 자막 기능이 비활성화되어 있어 분석할 수 없습니다."
        )

# 5. 알 수 없는 유튜브 에러 (네트워크 문제, IP 차단 등)
class YouTubeUnknownException(BusinessException):
    def __init__(self, debug_message: str = ""):
        # [추가] 받아온 디버그 메시지를 변수에 저장해둡니다.
        self.debug_message = debug_message

        super().__init__(
            code="YOUTUBE_ERROR",
            message="유튜브 자막을 가져오는 중 오류가 발생했습니다."
        )

#6. 유효하지 않은 유튜브 링크
class InvalidLinkException(BusinessException):
    def __init__(self):
        super().__init__(
            code="INVALID_LINK",
            message="유효하지 않은 유튜브 링크입니다. URL을 확인해주세요."
        )