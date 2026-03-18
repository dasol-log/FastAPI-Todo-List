from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from fastapi import Header, Cookie, Response  # ✅ 추가: Header, Cookie, Response import
from app.models.item import Todo, TodoCreate, TodoUpdate

router = APIRouter()

# 임시 저장소(DB 대신 사용)
todos = []
next_id = 1


# 전체 조회 + 검색/필터
@router.get(
    "/todos",
    response_model=list[Todo],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "전체 Todo 목록 조회 성공"},
        400: {"description": "잘못된 정렬 값 요청"}
    }
)
def get_todos(
    keyword: Optional[str] = Query(
        None,
        min_length=1,
        max_length=100,
        description="제목에서 검색할 키워드"
    ),
    done: Optional[bool] = Query(
        None,
        description="완료 여부로 필터링 (true/false)"
    ),
    sort: Optional[str] = Query(
		None,  
		description="정렬 방식 (asc 또는 desc)"  
	)
):
    # 원본 리스트를 기준으로 필터링 시작
    result = todos

    # keyword가 있으면 title에 포함된 Todo만 조회
    if keyword is not None:
        result = [todo for todo in result if keyword.lower() in todo.title.lower()]

    # done 값이 있으면 완료 여부로 필터링
    if done is not None:
        result = [todo for todo in result if todo.done == done]
    
    if sort is not None and sort not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort 값은 asc 또는 desc만 사용할 수 있습니다."
        )

    # id 기준 오름차순 정렬
    if sort == "asc":
        result = sorted(result, key=lambda todo: todo.id)

    # id 기준 내림차순 정렬
    elif sort == "desc":
        result = sorted(result, key=lambda todo: todo.id, reverse=True)

    return result


# 상세 조회
@router.get(
    "/todos/{todo_id}",
    response_model=Todo,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Todo 상세 조회 성공"},
        404: {"description": "해당 Todo를 찾을 수 없음"}
    }
)
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="해당 할 일이 없습니다."
    )


# 생성
@router.post(
    "/todos",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Todo 생성 성공"},
        400: {"description": "중복된 제목 또는 잘못된 요청"}
    }
)
def create_todo(todo_data: TodoCreate):
    global next_id

    for todo in todos:
        if todo.title == todo_data.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="같은 제목의 할 일은 이미 존재합니다."
            )

    new_todo = Todo(
        id=next_id,
        title=todo_data.title,
        done=todo_data.done
    )

    todos.append(new_todo)
    next_id += 1
    return new_todo


# 수정
@router.put(
    "/todos/{todo_id}",
    response_model=Todo,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Todo 수정 성공"},
        400: {"description": "수정할 데이터가 없거나 잘못된 요청"},
        404: {"description": "수정할 Todo를 찾을 수 없음"}
    }
)
def update_todo(todo_id: int, todo_data: TodoUpdate):
    update_data = todo_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 데이터를 하나 이상 보내주세요."
        )

    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            updated_todo = todo.model_copy(
                update=update_data
            )
            todos[index] = updated_todo
            return updated_todo

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="수정할 할 일이 없습니다."
    )


# 삭제
@router.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Todo 삭제 성공"},
        404: {"description": "삭제할 Todo를 찾을 수 없음"}
    }
)
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            deleted_todo = todos.pop(index)
            return {
                "message": "삭제 완료",
                "deleted": deleted_todo
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="삭제할 할 일이 없습니다."
    )

# ✅ 추가: Header 읽기 예제
@router.get("/headers-demo")
def read_headers(
    user_agent: Optional[str] = Header(None),   # 요청 헤더의 User-Agent 읽기
    x_token: Optional[str] = Header(None)       # 커스텀 헤더 X-Token 읽기
):
    return {
        "message": "요청 헤더를 읽었습니다.",
        "user_agent": user_agent,
        "x_token": x_token
    }


# ✅ 추가: Cookie 저장 예제
@router.post("/cookies-demo")
def create_cookie(response: Response):
    response.set_cookie(
        key="visit_user",
        value="fastapi-student",
        httponly=True  # 자바스크립트에서 직접 접근 어렵게 설정
    )
    return {
        "message": "쿠키가 저장되었습니다.",
        "cookie_name": "visit_user",
        "cookie_value": "fastapi-student"
    }


# ✅ 추가: Cookie 읽기 예제
@router.get("/cookies-demo")
def read_cookie(visit_user: Optional[str] = Cookie(None)):
    return {
        "message": "쿠키를 읽었습니다.",
        "visit_user": visit_user
    }