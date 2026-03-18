from fastapi import APIRouter, HTTPException
from app.models.item import Todo, TodoCreate, TodoUpdate

router = APIRouter()

# 임시 저장소(DB 대신 사용)
todos = []
next_id = 1


# 전체 조회
@router.get("/todos", response_model=list[Todo])
def get_todos():
    return todos


# 상세 조회
@router.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="해당 할 일이 없습니다.")


# 생성
@router.post("/todos", response_model=Todo)
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