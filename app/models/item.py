from pydantic import BaseModel, Field  # ✅ 수정: Field 추가
from typing import Optional


# 할 일 생성할 때 사용하는 데이터 형식
class TodoCreate(BaseModel):  # 요청 데이터 검증 (POST)
    # ✅ title에 검증 추가
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    done: bool = False


# 할 일 수정할 때 사용하는 데이터 형식
class TodoUpdate(BaseModel):  # 수정 데이터 검증 (PUT/PATCH)
    # ✅ 수정할 때도 title 검증 추가
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="수정할 할 일 제목")
    done: Optional[bool] = None


# 실제 저장/응답에 사용하는 데이터 형식
class Todo(BaseModel):  # 응답 데이터 형식 정의
    id: int
    # ✅ 응답 모델에도 같은 구조를 맞춰줌
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    done: bool = False