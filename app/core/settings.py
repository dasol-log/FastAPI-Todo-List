# ✅ 추가: 프로젝트 설정 전용 파일

class Settings:
    PROJECT_NAME: str = "FastAPI Todo API"
    VERSION: str = "2.1.0"
    DATABASE_URL: str = "sqlite:///./todo.db"
    ALLOWED_ORIGINS: list[str] = ["*"]


# ✅ 추가: 설정 객체 생성
settings = Settings()