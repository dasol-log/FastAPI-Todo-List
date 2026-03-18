from pydantic import BaseModel
from typing import Optional


# 할 일 생성할 때 사용하는 데이터 형식
class TodoCreate(BaseModel):  # 요청 데이터 검증 (POST)
    title: str
    done: bool = False


# 할 일 수정할 때 사용하는 데이터 형식
class TodoUpdate(BaseModel):  # 수정 데이터 검증 (PUT/PATCH)
    title: Optional[str] = None
    done: Optional[bool] = None


# 실제 저장/응답에 사용하는 데이터 형식
class Todo(BaseModel):  # 응답 데이터 형식 정의 (JSON 직렬화) JSON으로 변환하는 것을 의미
    id: int
    title: str
    done: bool = False