# ✅ 추가: DB 연결 / 세션 관리 전용 파일

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings


# ✅ 추가: SQLite 연결 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용 옵션
)

# ✅ 추가: 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ✅ 추가: FastAPI Depends에서 사용할 DB 세션 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()