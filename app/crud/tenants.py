from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate


def get(db: Session, tenant_id: int) -> Tenant | None:
    return db.get(Tenant, tenant_id)


def get_by_slug(db: Session, slug: str) -> Tenant | None:
    return db.execute(select(Tenant).where(Tenant.slug == slug)).scalar_one_or_none()


def create(db: Session, *, obj_in: TenantCreate) -> Tenant:
    db_obj = Tenant(name=obj_in.name, slug=obj_in.slug)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

