from fastapi import FastAPI
from app.core.config import engine, Base
import uvicorn

app = FastAPI(title="Hackaton")

from fastapi.middleware.cors import CORSMiddleware

origins = [
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중엔 * 로 두고, 배포 시 특정 도메인만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": ""}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
