# 테이블 생성 전용 파일

from app.db.base import Base
from app.db.session import engine

# 모델 import 해야 Base.metadata에 등록됨
from app.models.todo import TodoDB   # noqa: F401
from app.models.user import UserDB   # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)