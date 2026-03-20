# 프로젝트 설정 전용 파일
import os  # ✅ 추가

class Settings:
    PROJECT_NAME: str = "FastAPI Todo API"
    VERSION: str = "2.2.0"
    DATABASE_URL: str = "sqlite:///./todo.db"
    ALLOWED_ORIGINS: list[str] = ["*"]


    # ✅ 추가: 업로드 기본 폴더
    MEDIA_ROOT: str = "media"

    # ✅ 추가: Todo 이미지 저장 폴더
    TODO_UPLOAD_DIR: str = os.path.join(MEDIA_ROOT, "todos")

    # JWT 설정
    SECRET_KEY: str = "my-super-secret-key"   # 나중에는 더 복잡하게 바꾸기
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

# 설정 객체 생성
settings = Settings()