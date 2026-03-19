from fastapi import APIRouter, HTTPException, status, Query, Depends, BackgroundTasks  # [추가] BackgroundTasks import
from typing import Optional
from sqlalchemy.orm import Session
import asyncio  # [추가] async / await 연습용

from app.schemas.todo import Todo, TodoCreate, TodoUpdate
from app.models.todo import TodoDB
from app.models.user import UserDB
from app.db.session import get_db
from app.routes.user import get_current_user

# [추가] 백그라운드 작업 함수 import
from app.tasks.todo_tasks import write_todo_log, fake_send_notification

router = APIRouter(prefix="/todos", tags=["Todos"])


# [추가] async / await 연습용 비동기 API
# - DB 작업이 아니라 "비동기 대기" 흐름을 보기 위한 예제입니다.
# - await asyncio.sleep() 는 "기다리는 동안 다른 작업 가능" 상태를 의미합니다.
@router.get("/async-preview")
async def async_preview():
    await asyncio.sleep(2)  # [추가] 비동기 대기
    return {"message": "2초 비동기 대기 후 응답이 완료되었습니다."}


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


# =========================================================
# 내 Todo 상세 조회
# =========================================================
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


# =========================================================
# 내 Todo 생성
# - [추가] BackgroundTasks 사용
# - 응답 후 로그 저장, 알림 기록 작업을 뒤에서 실행
# =========================================================
@router.post("", response_model=Todo, status_code=201)
def create_todo(
    todo_data: TodoCreate,
    background_tasks: BackgroundTasks,  # [추가] 백그라운드 작업 객체
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

    # =====================================================
    # [추가] 응답 후 실행할 작업 등록
    # - add_task()에 넣으면 사용자 응답이 끝난 뒤 실행됩니다.
    # =====================================================
    background_tasks.add_task(
        write_todo_log,
        "CREATE",
        current_user.username,
        new_todo.title
    )

    background_tasks.add_task(
        fake_send_notification,
        current_user.username,
        f"'{new_todo.title}' Todo가 생성되었습니다."
    )

    return new_todo


# =========================================================
# 내 Todo 수정
# - [추가] 수정 후 로그 저장
# =========================================================
@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    background_tasks: BackgroundTasks,  # [추가]
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

    # [추가] 수정 로그 백그라운드 저장
    background_tasks.add_task(
        write_todo_log,
        "UPDATE",
        current_user.username,
        todo.title
    )

    return todo


# =========================================================
# 내 Todo 삭제
# - [추가] 삭제 후 로그 저장
# =========================================================
@router.delete("/{todo_id}", status_code=200)
def delete_todo(
    todo_id: int,
    background_tasks: BackgroundTasks,  # [추가]
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

    # [추가] 삭제 로그 백그라운드 저장
    background_tasks.add_task(
        write_todo_log,
        "DELETE",
        current_user.username,
        deleted_title
    )

    return {
        "message": "삭제 완료",
        "deleted": deleted_data
    }

