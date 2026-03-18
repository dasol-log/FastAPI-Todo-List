from pydantic import BaseModel, Field
from typing import Optional


# 할 일 생성할 때 사용하는 데이터 형식
class TodoCreate(BaseModel):  # 요청 데이터 검증 (POST)
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    done: bool = False


# 할 일 수정할 때 사용하는 데이터 형식
class TodoUpdate(BaseModel):  # 수정 데이터 검증 (PUT/PATCH)
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="수정할 할 일 제목")
    done: Optional[bool] = None


# 실제 저장/응답에 사용하는 데이터 형식
class Todo(BaseModel):  # 응답 데이터 형식 정의
    id: int
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    done: bool = False