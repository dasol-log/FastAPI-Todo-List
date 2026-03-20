from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.base import Base


class TodoDB(Base):
    __tablename__ = "todos"   # 실제 DB 테이블명

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ✅ 추가: 업로드한 이미지 경로 저장
    image_path = Column(String(255), nullable=True)