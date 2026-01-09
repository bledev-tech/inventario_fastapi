from __future__ import annotations

import re
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.tenant import TenantCreate
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", value).strip().lower()
    collapsed = re.sub(r"[\s_-]+", "-", cleaned)
    return collapsed.strip("-")


@router.post("/token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = crud.users.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        detail = error_detail("invalid_credentials", "Incorrect email or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
    if not user.is_active:
        detail = error_detail("user_inactive", "Inactive user")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    tenant = crud.tenants.get(db, user.tenant_id)
    if tenant and not tenant.is_active:
        detail = error_detail("tenant_inactive", "Tenant is inactive")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    access_token = create_access_token(
        subject=user.id,
        tenant_id=user.tenant_id,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_tenant_and_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserOut:
    if not settings.allow_user_signup:
        detail = error_detail("signup_disabled", "Self signup is disabled")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    if crud.users.get_by_email(db, payload.email):
        detail = error_detail("email_in_use", "Email already registered")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    raw_slug = payload.tenant_slug or payload.tenant_name
    slug = _slugify(raw_slug)
    if not slug:
        detail = error_detail("invalid_slug", "Tenant slug is required")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    if crud.tenants.get_by_slug(db, slug):
        detail = error_detail("tenant_slug_in_use", "Tenant slug already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    tenant = crud.tenants.create(db, obj_in=TenantCreate(name=payload.tenant_name, slug=slug))
    user_in = UserCreate(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        is_superuser=True,
    )
    user = crud.users.create(db, obj_in=user_in, tenant_id=tenant.id)
    return user


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user
