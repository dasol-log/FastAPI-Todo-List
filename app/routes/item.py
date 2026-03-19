from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional
from fastapi import Header, Cookie, Response
from sqlalchemy.orm import Session

# ✅ 수정: 기존 Pydantic 모델 import 위치 변경
from app.schemas.todo import Todo, TodoCreate, TodoUpdate

# ✅ 추가: DB 모델 import
from app.models.todo import TodoDB

# ✅ 추가: DB 세션 import
from app.database import get_db

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
    ),
    db: Session = Depends(get_db)   # ✅ 추가: DB 세션 주입
):
    # ✅ 추가: DB 쿼리 시작
    query = db.query(TodoDB)

    # keyword 검색
    if keyword is not None:
        query = query.filter(TodoDB.title.ilike(f"%{keyword}%"))

    # done 필터
    if done is not None:
        query = query.filter(TodoDB.done == done)

    # 정렬 검사
    if sort is not None and sort not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort 값은 asc 또는 desc만 사용할 수 있습니다."
        )

    # 정렬
    if sort == "asc":
        query = query.order_by(TodoDB.id.asc())
    elif sort == "desc":
        query = query.order_by(TodoDB.id.desc())
    else:
        query = query.order_by(TodoDB.id.asc())

    # ✅ 추가: DB에서 결과 조회
    todos = query.all()
    return todos


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
def get_todo(todo_id: int, db: Session = Depends(get_db)):   # ✅ 추가
    # ✅ 추가: DB에서 1개 조회
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 할 일이 없습니다."
        )

    return todo


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
def create_todo(todo_data: TodoCreate, db: Session = Depends(get_db)):   # ✅ 추가
    # ✅ 추가: 중복 제목 확인
    existing_todo = db.query(TodoDB).filter(TodoDB.title == todo_data.title).first()
    if existing_todo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="같은 제목의 할 일은 이미 존재합니다."
        )

    # ✅ 추가: DB 객체 생성
    new_todo = TodoDB(
        title=todo_data.title,
        done=todo_data.done
    )

    # ✅ 추가: DB 저장
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

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
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db)   # ✅ 추가
):
    # 수정 데이터 확인
    update_data = todo_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 데이터를 하나 이상 보내주세요."
        )

    # ✅ 추가: DB에서 대상 찾기
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수정할 할 일이 없습니다."
        )

    # ✅ 추가: title 중복 검사
    if "title" in update_data:
        duplicate_todo = (
            db.query(TodoDB)
            .filter(TodoDB.title == update_data["title"], TodoDB.id != todo_id)
            .first()
        )
        if duplicate_todo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="같은 제목의 다른 할 일이 이미 존재합니다."
            )

    # ✅ 추가: 값 반영
    for key, value in update_data.items():
        setattr(todo, key, value)

    db.commit()
    db.refresh(todo)

    return todo


# 삭제
@router.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Todo 삭제 성공"},
        404: {"description": "삭제할 Todo를 찾을 수 없음"}
    }
)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):   # ✅ 추가
    # ✅ 추가: DB에서 삭제 대상 찾기
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 할 일이 없습니다."
        )

    deleted_data = {
        "id": todo.id,
        "title": todo.title,
        "done": todo.done
    }

    # ✅ 추가: DB 삭제
    db.delete(todo)
    db.commit()

    return {
        "message": "삭제 완료",
        "deleted": deleted_data
    }


# Header 읽기 예제
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


# Cookie 저장 예제
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


# Cookie 읽기 예제
@router.get("/cookies-demo")
def read_cookie(visit_user: Optional[str] = Cookie(None)):
    return {
        "message": "쿠키를 읽었습니다.",
        "visit_user": visit_user
    }