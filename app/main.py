from fastapi import FastAPI, Request  # ✅ 추가: Request import
from fastapi.responses import JSONResponse  # ✅ 추가: JSONResponse import
from fastapi.exceptions import RequestValidationError  # ✅ 추가: 검증 예외 import
from app.routes.item import router as item_router

app = FastAPI(
    title="FastAPI Todo API",
    description="Pydantic 검증과 Path / Query Parameter가 포함된 Todo CRUD API",  # ✅ 수정: 설명 문구 변경
    version="1.2.0"  # ✅ 수정: 버전 변경
)

# 라우터 등록
app.include_router(item_router)

@app.get("/")
def home():
    return {"message": "FastAPI Todo API 실행 중"}


# ✅ 추가: 요청 데이터 검증 실패 시 에러 메시지 통일
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "입력값 검증에 실패했습니다.",
            "errors": exc.errors()
        }
    )