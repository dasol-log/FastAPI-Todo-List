from fastapi import FastAPI
from app.routes.item import router as item_router

app = FastAPI(
    title="FastAPI Todo API",                 # ✅ 문서 제목 추가
    description="Pydantic 검증이 포함된 Todo CRUD API",  # ✅ 문서 설명 추가
    version="1.0.0"                          # ✅ 버전 추가
)

# 라우터 등록
app.include_router(item_router)

@app.get("/")
def home():
    return {"message": "FastAPI Todo API 실행 중"}