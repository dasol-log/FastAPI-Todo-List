# ✅ 추가: 회원가입 API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib

from app.db.session import get_db
from app.models.user import UserDB
from app.schemas.user import UserCreate, User

router = APIRouter(prefix="/users", tags=["Users"])   # ✅ 추가


# ✅ 추가: 비밀번호 해시 함수
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ✅ 추가: 회원가입 API
@router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "회원가입 성공"},
        400: {"description": "이미 존재하는 사용자명"}
    }
)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # 같은 username 존재 여부 확인
    existing_user = db.query(UserDB).filter(UserDB.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 username입니다."
        )

    # 비밀번호 해시 처리
    hashed_pw = hash_password(user_data.password)

    # DB 저장용 객체 생성
    new_user = UserDB(
        username=user_data.username,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user