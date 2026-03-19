# 회원가입 API

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # ✅ 추가
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone # ✅ 추가
import hashlib
import jwt # ✅ 추가

from app.db.session import get_db
from app.models.user import UserDB
from app.schemas.user import UserCreate, User, UserLogin, Token, UserInfo # ✅ 추가
from app.core.settings import settings # ✅ 추가

router = APIRouter(prefix="/users", tags=["Users"])   # ✅ 추가

# ✅ 추가: Bearer 토큰 추출 도구
security = HTTPBearer()


# 비밀번호 해시 함수
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ✅ 추가: JWT 생성 함수
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# ✅ 추가: 현재 사용자 조회 함수
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str | None = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다."
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 검증에 실패했습니다."
        )

    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )

    return user


# 회원가입 API
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


# ✅ 추가: 로그인 API
@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "아이디 또는 비밀번호 불일치"}
    }
)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == user_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다."
        )

    hashed_input_password = hash_password(user_data.password)

    if user.password != hashed_input_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다."
        )

    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ✅ 추가: 로그인한 사용자 정보 조회
@router.get(
    "/me",
    response_model=UserInfo,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "현재 로그인 사용자 조회 성공"},
        401: {"description": "인증 실패"}
    }
)
def read_me(current_user: UserDB = Depends(get_current_user)):
    return current_user