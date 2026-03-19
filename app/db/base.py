# ✅ 추가: SQLAlchemy Base 분리

from sqlalchemy.orm import declarative_base

# ✅ 추가: 모든 ORM 모델의 부모 클래스
Base = declarative_base()