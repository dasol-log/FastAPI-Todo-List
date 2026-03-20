from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Query,
    Depends,
    BackgroundTasks,
    UploadFile,   # ✅ 추가
    File,         # ✅ 추가
    Form          # ✅ 추가
)
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.todo import Todo, TodoCreate, TodoUpdate
from app.models.todo import TodoDB
from app.models.user import UserDB
from app.db.session import get_db
from app.routes.user import get_current_user

# ✅ 추가: 파일 저장 유틸 import
from app.utils.file_handler import save_uploaded_image, delete_uploaded_file


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


# ✅ 수정: 내 Todo 생성 + 이미지 업로드
# - form-data 방식 사용
# - title, done, image를 함께 전송 가능
@router.post("", response_model=Todo, status_code=201)
def create_todo(
    title: str = Form(...),                    # ✅ 수정
    done: bool = Form(False),                 # ✅ 수정
    image: UploadFile | None = File(None),    # ✅ 추가
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    existing_todo = (
        db.query(TodoDB)
        .filter(
            TodoDB.title == title,
            TodoDB.user_id == current_user.id
        )
        .first()
    )

    if existing_todo:
        raise HTTPException(
            status_code=400,
            detail="같은 제목의 할 일이 이미 존재합니다."
        )

    image_path = None

    # ✅ 추가: 이미지가 있으면 저장
    if image is not None and image.filename:
        image_path = save_uploaded_image(image)

    new_todo = TodoDB(
        title=title,
        done=done,
        user_id=current_user.id,
        image_path=image_path  # ✅ 추가
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


# ✅ 수정: 내 Todo 수정 + 이미지 교체 가능
# - title / done / image 중 일부만 보내도 됨
@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    background_tasks: BackgroundTasks,
    title: Optional[str] = Form(None),                # ✅ 수정
    done: Optional[bool] = Form(None),                # ✅ 수정
    image: UploadFile | None = File(None),            # ✅ 추가
    delete_image: bool = Form(False),        # ✅ 추가
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    todo = (
        db.query(TodoDB)
        .filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(status_code=404, detail="수정할 할 일이 없습니다.")

    if title is None and done is None and image is None and not delete_image:
        raise HTTPException(
            status_code=400,
            detail="수정할 데이터를 하나 이상 보내주세요."
        )

    # ✅ 추가: 제목 중복 검사
    if title is not None:
        duplicate_todo = (
            db.query(TodoDB)
            .filter(
                TodoDB.title == title,
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
        todo.title = title

    # ✅ 추가: done 수정
    if done is not None:
        todo.done = done

    # ✅ 추가: 이미지 삭제 처리 (새 이미지 업로드 앞에 위치)
    if delete_image and todo.image_path:
        delete_uploaded_file(todo.image_path)
        todo.image_path = None

    # ✅ 추가: 새 이미지 업로드 시 기존 파일 삭제 후 교체
    if image is not None and image.filename:
        delete_uploaded_file(todo.image_path)
        todo.image_path = save_uploaded_image(image)

    db.commit()
    db.refresh(todo)

    return todo

# ✅ Todo 이미지 삭제 전용 API
@router.delete("/{todo_id}/image", status_code=200)
def delete_todo_image(
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

    if not todo.image_path:
        raise HTTPException(status_code=400, detail="삭제할 이미지가 없습니다.")

    delete_uploaded_file(todo.image_path)
    todo.image_path = None

    db.commit()
    db.refresh(todo)

    return {
        "message": "이미지 삭제 완료",
        "todo_id": todo.id
    }


# Todo 삭제
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

    deleted_data = {
        "id": todo.id,
        "title": todo.title,
        "done": todo.done,
        "user_id": todo.user_id,
        "image_path": todo.image_path
    }

    delete_uploaded_file(todo.image_path)

    db.delete(todo)
    db.commit()

    return {
        "message": "삭제 완료",
        "deleted": deleted_data
    }