from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_active_superuser, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def list_users(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> list[UserOut]:
    return crud.users.get_multi_by_tenant(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> UserOut:
    if crud.users.get_by_email(db, user_in.email):
        detail = error_detail("email_in_use", "Email already registered")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    return crud.users.create(db, obj_in=user_in, tenant_id=current_user.tenant_id)

