from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
import asyncio  # [추가] async / await 연습용

from app.schemas.todo import Todo, TodoCreate, TodoUpdate
from app.models.todo import TodoDB
from app.models.user import UserDB
from app.db.session import get_db
from app.routes.user import get_current_user


router = APIRouter(prefix="/todos", tags=["Todos"])


# 내 Todo 목록 조회
# - 로그인한 사용자의 Todo만 조회
@router.get(
    "",
    response_model=list[Todo],
    status_code=status.HTTP_200_OK
)
def get_todos(
    keyword: Optional[str] = Query(None, min_length=1, max_length=100, description="제목 검색"),
    done: Optional[bool] = Query(None, description="완료 여부"),
    sort: Optional[str] = Query(None, description="asc 또는 desc"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    query = db.query(TodoDB).filter(TodoDB.user_id == current_user.id)

    if keyword is not None:
        query = query.filter(TodoDB.title.ilike(f"%{keyword}%"))

    if done is not None:
        query = query.filter(TodoDB.done == done)

    if sort is not None and sort not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort 값은 asc 또는 desc만 사용할 수 있습니다."
        )

    if sort == "asc":
        query = query.order_by(TodoDB.id.asc())
    elif sort == "desc":
        query = query.order_by(TodoDB.id.desc())
    else:
        query = query.order_by(TodoDB.id.asc())

    return query.all()


# 내 Todo 상세 조회
@router.get("/{todo_id}", response_model=Todo)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    todo = (
        db.query(TodoDB)
        .filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(status_code=404, detail="해당 할 일이 없습니다.")

    return todo


# 내 Todo 생성
@router.post("", response_model=Todo, status_code=201)
def create_todo(
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    existing_todo = (
        db.query(TodoDB)
        .filter(
            TodoDB.title == todo_data.title,
            TodoDB.user_id == current_user.id
        )
        .first()
    )

    if existing_todo:
        raise HTTPException(
            status_code=400,
            detail="같은 제목의 할 일이 이미 존재합니다."
        )

    new_todo = TodoDB(
        title=todo_data.title,
        done=todo_data.done,
        user_id=current_user.id
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


# 내 Todo 수정
@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    update_data = todo_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="수정할 데이터를 하나 이상 보내주세요."
        )

    todo = (
        db.query(TodoDB)
        .filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(status_code=404, detail="수정할 할 일이 없습니다.")

    if "title" in update_data:
        duplicate_todo = (
            db.query(TodoDB)
            .filter(
                TodoDB.title == update_data["title"],
                TodoDB.user_id == current_user.id,
                TodoDB.id != todo_id
            )
            .first()
        )
        if duplicate_todo:
            raise HTTPException(
                status_code=400,
                detail="같은 제목의 다른 할 일이 이미 존재합니다."
            )

    for key, value in update_data.items():
        setattr(todo, key, value)

    db.commit()
    db.refresh(todo)

    return todo


# 내 Todo 삭제
@router.delete("/{todo_id}", status_code=200)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    todo = (
        db.query(TodoDB)
        .filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(status_code=404, detail="삭제할 할 일이 없습니다.")

    deleted_title = todo.title

    deleted_data = {
        "id": todo.id,
        "title": todo.title,
        "done": todo.done,
        "user_id": todo.user_id
    }

    db.delete(todo)
    db.commit()

    return {
        "message": "삭제 완료",
        "deleted": deleted_data
    }

