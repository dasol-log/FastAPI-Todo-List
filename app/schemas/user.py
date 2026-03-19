# User 요청/응답 스키마

from pydantic import BaseModel, Field


# 회원가입 요청용
class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="회원 아이디")
    password: str = Field(..., min_length=4, max_length=100, description="회원 비밀번호")


# 회원가입 응답용
class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# ✅ 추가: 로그인 요청용
class UserLogin(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="회원 아이디")
    password: str = Field(..., min_length=4, max_length=100, description="회원 비밀번호")


# ✅ 추가: 토큰 응답용
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ✅ 추가: 현재 로그인 사용자 응답용
class UserInfo(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True