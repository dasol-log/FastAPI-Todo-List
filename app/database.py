# ✅ 추가: 데이터베이스 연결 설정 파일

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ 추가: SQLite DB 주소
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# ✅ 추가: SQLite는 check_same_thread=False 옵션 필요
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ✅ 추가: DB 세션 생성기
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ✅ 추가: ORM 모델들의 부모 클래스
Base = declarative_base()


# ✅ 추가: 요청마다 DB 세션 열고 닫는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()