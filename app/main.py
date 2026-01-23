# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# [수정] 라우터 임포트는 맨 위로 올리는 것이 정석입니다.
from app.routers import video 



# 서버 시작할 때 .env 파일을 읽어옴
load_dotenv()

app = FastAPI(
    title="QuickEng Server",
    description="YouTube Shorts 기반 영어 학습 앱 QuickEng의 백엔드 서버입니다.",
    version="0.1.0"
)

# =============================================================================
# CORS 설정 (Android 앱 통신용)
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# 라우터 등록
# =============================================================================
# video.py 안에서 prefix="/v1/video"를 이미 설정했으므로, 
# 여기서는 그냥 추가만 해주면 됩니다.
app.include_router(video.router)


# =============================================================================
# 기본 엔드포인트
# =============================================================================
@app.get("/")
def read_root():
    """서버 상태 확인용 루트 경로"""
    return {"message": "QuickEng Server is running!", "status": "active"}

@app.get("/health")
def health_check():
    """
    [헬스 체크] AWS/GCP 로드밸런서나 모니터링 도구가
    서버가 살았는지 죽었는지 찌러보는 용도입니다.
    """
    return {"status": "ok"}