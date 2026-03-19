# ✅ 추가: SQLAlchemy 테이블 모델

from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class TodoDB(Base):
    __tablename__ = "todos"   # ✅ 추가: 실제 DB 테이블명

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True, index=True)
    done = Column(Boolean, default=False)