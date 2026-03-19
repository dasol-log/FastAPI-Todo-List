from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
# ✅ 수정: Base import 위치 변경
from app.db.base import Base


class TodoDB(Base):
    __tablename__ = "todos"   # 실제 DB 테이블명

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True, index=True)
    done = Column(Boolean, default=False)
    # ✅ 추가: 어떤 사용자의 Todo인지 저장
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)