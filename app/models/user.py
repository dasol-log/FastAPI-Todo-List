# ✅ 추가: User DB 모델

from sqlalchemy import Column, Integer, String
from app.db.base import Base


class UserDB(Base):
    __tablename__ = "users"   # ✅ 추가: users 테이블 생성

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)   # ✅ 추가: 해시된 비밀번호 저장