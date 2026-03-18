from fastapi import APIRouter, HTTPException, status, Query  # ✅ Query 추가
from typing import Optional  # ✅ Optional 추가
from app.models.item import Todo, TodoCreate, TodoUpdate

router = APIRouter()

# 임시 저장소(DB 대신 사용)
todos = []
next_id = 1


# 전체 조회 + 검색/필터
@router.get("/todos", response_model=list[Todo])
def get_todos(
    keyword: Optional[str] = Query(
        None,
        min_length=1,
        max_length=100,
        description="제목에서 검색할 키워드"
    ),  # ✅ Query parameter - 제목 검색
    done: Optional[bool] = Query(
        None,
        description="완료 여부로 필터링 (true/false)"
    ),  # ✅ Query parameter - 완료 여부 필터
    sort: Optional[str] = Query( # ✅ 추가: 정렬 기능  
		None,  
		description="정렬 방식 (asc 또는 desc)"  
	)
):
    # ✅ 추가: 원본 리스트를 기준으로 필터링 시작
    result = todos

    # ✅ keyword가 있으면 title에 포함된 Todo만 조회
    if keyword is not None:
        result = [todo for todo in result if keyword.lower() in todo.title.lower()]

    # ✅ done 값이 있으면 완료 여부로 필터링
    if done is not None:
        result = [todo for todo in result if todo.done == done]
    
    # ✅ 추가: 정렬 기능  
	# id 기준 오름차순 정렬  
    if sort == "asc":  
        result = sorted(result, key=lambda todo: todo.id)  
  
	# ✅ 추가: 정렬 기능  
	# id 기준 내림차순 정렬  
    elif sort == "desc":  
        result = sorted(result, key=lambda todo: todo.id, reverse=True)

    return result


# 상세 조회
@router.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="해당 할 일이 없습니다.")


# 생성
@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)  
# ✅ 생성 성공 시 201 상태코드로 변경
def create_todo(todo_data: TodoCreate):
    global next_id

    new_todo = Todo(
        id=next_id,
        title=todo_data.title,
        done=todo_data.done
    )

    todos.append(new_todo)
    next_id += 1
    return new_todo


# 수정
@router.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_data: TodoUpdate):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            updated_todo = todo.model_copy(
                update=todo_data.model_dump(exclude_unset=True)
            )
            todos[index] = updated_todo
            return updated_todo

    raise HTTPException(status_code=404, detail="수정할 할 일이 없습니다.")


# 삭제
@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            deleted_todo = todos.pop(index)
            return {"message": "삭제 완료", "deleted": deleted_todo}

    raise HTTPException(status_code=404, detail="삭제할 할 일이 없습니다.")