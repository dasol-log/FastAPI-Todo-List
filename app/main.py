from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # ✅ 추가: CORS 미들웨어 import
from app.routes.item import router as item_router

app = FastAPI(
    title="FastAPI Todo API",
    description="Pydantic 검증과 Path / Query Parameter가 포함된 Todo CRUD API",
    version="1.3.0"  # ✅ 추가: 버전 수정
)

# ✅ 추가: CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 학습용: 모든 출처 허용
    allow_credentials=True,       # 쿠키/인증정보 포함 허용
    allow_methods=["*"],          # 모든 HTTP 메서드 허용
    allow_headers=["*"],          # 모든 헤더 허용
)

# 라우터 등록
app.include_router(item_router)

@app.get("/")
def home():
    return {"message": "FastAPI Todo API 실행 중"}


# 요청 데이터 검증 실패 시 에러 메시지 통일
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "입력값 검증에 실패했습니다.",
            "errors": exc.errors()
        }
    )