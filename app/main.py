from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os  # ✅ 추가

from app.routes.item import router as item_router
from app.routes.user import router as user_router

from app.core.settings import settings
from app.db.init_db import init_db

# ✅ 추가: media 폴더 자동 생성
os.makedirs(settings.TODO_UPLOAD_DIR, exist_ok=True)

# 앱 시작 전에 DB 초기화
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI + SQLAlchemy 기반 Todo CRUD API",
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 학습용: 모든 출처 허용
    allow_credentials=True,       # 쿠키/인증정보 포함 허용
    allow_methods=["*"],          # 모든 HTTP 메서드 허용
    allow_headers=["*"],          # 모든 헤더 허용
)

# 라우터 등록
app.include_router(item_router)
app.include_router(user_router)

# static 폴더 연결
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 추가: 업로드 파일 접근용 mount
app.mount("/media", StaticFiles(directory="media"), name="media")

# 템플릿 폴더 설정
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def home():
    return {"message": "FastAPI Todo API 실행 중 (이미지 업로드 기능 추가 완료)"}


@app.get("/page")
def todo_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# ✅ 삭제: HTML 페이지 렌더링을 위해
# @app.get("/")
# def home():
    # return {"message": "FastAPI Todo API 실행 중"}


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