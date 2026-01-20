#!/usr/bin/env python
"""
ngrok을 사용하여 로컬 서버를 외부에 노출합니다.
"""
from pyngrok import ngrok

# ngrok 설정
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")  # https://dashboard.ngrok.com에서 토큰 발급

# 8000 포트 외부 노출
public_url = ngrok.connect(8000)
print(f"ngrok 공개 URL: {public_url}")

# 트래픽 로깅
ngrok_logs = ngrok.get_ngrok_logs()
print("ngrok 시작됨. Ctrl+C로 종료하세요.")

try:
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("\nngrok 종료 중...")
    ngrok.kill()
