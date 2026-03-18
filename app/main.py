from fastapi import FastAPI
from app.routes.item import router as item_router

app = FastAPI(
    title="FastAPI Todo API",
    description="Pydantic 검증과 Path / Query Parameter가 포함된 Todo CRUD API",  # ✅ 수정: 설명 문구 변경
    version="1.1.0"  # ✅ 수정: 버전 변경
)

# 라우터 등록
app.include_router(item_router)

@app.get("/")
def home():
    return {"message": "FastAPI Todo API 실행 중"}