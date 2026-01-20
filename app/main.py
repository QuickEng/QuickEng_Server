# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="QuickEng Server",
    description="YouTube Shorts 기반 영어 학습 앱 QuickEng의 백엔드 서버입니다.",
    version="0.1.0"
)

# CORS 설정 (Android 앱과 통신하기 위해 필수)
# 현재는 모든 출처(*)를 허용하지만, 배포 시에는 보안을 위해 수정해야 합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "QuickEng Server is running!", "status": "active"}

# 헬스 체크용 엔드포인트
@app.get("/health")
def health_check():
    return {"status": "ok"}
