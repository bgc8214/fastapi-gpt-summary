import os
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from starlette.responses import StreamingResponse
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("🚨 OpenAI API Key가 설정되지 않았습니다. .env 파일을 확인하세요.")

app = FastAPI()
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ POST 요청으로 GPT-3.5 Turbo 요약 API (스트리밍 지원)
@app.post("/stream-summary/")
async def stream_summary(payload: dict):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="❌ 'text' 필드가 필요합니다.")

    def generate():
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"이 내용을 요약해줘: {text}"}],
                stream=True  # ✅ 스트리밍 응답 활성화
            )
            for chunk in response:  # ✅ `async for` 대신 `for` 사용
                if chunk.choices and chunk.choices[0].delta.content:
                    yield (chunk.choices[0].delta.content + "\n").encode("utf-8")
        except Exception as e:
            yield f"❌ Error: {str(e)}".encode("utf-8")

    return StreamingResponse(generate(), media_type="text/event-stream")
