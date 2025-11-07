from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaUpdate


def get(db: Session, persona_id: int) -> Persona | None:
    return db.get(Persona, persona_id)


def get_by_nombre(db: Session, nombre: str) -> Persona | None:
    stmt = select(Persona).where(Persona.nombre == nombre)
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[Persona]:
    stmt = select(Persona).order_by(Persona.nombre).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create(db: Session, *, obj_in: PersonaCreate) -> Persona:
    db_obj = Persona(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Persona, obj_in: PersonaUpdate) -> Persona:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: Persona) -> None:
    db.delete(db_obj)
    db.commit()
