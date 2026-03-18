from fastapi import FastAPI
from app.routes.item import router as item_router

app = FastAPI()

# 라우터 등록
app.include_router(item_router)

@app.get("/")
def home():
    return {"message": "FastAPI Todo API 실행 중"}