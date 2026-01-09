from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.persona import PersonaCreate, PersonaOut, PersonaUpdate

router = APIRouter()


@router.get("/", response_model=list[PersonaOut])
def read_personas(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PersonaOut]:
    return crud.personas.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=PersonaOut, status_code=status.HTTP_201_CREATED)
def create_persona(
    *,
    persona_in: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PersonaOut:
    existente = crud.personas.get_by_nombre(
        db,
        tenant_id=current_user.tenant_id,
        nombre=persona_in.nombre,
    )
    if existente:
        detail = error_detail(
            "persona_duplicate",
            "Ya existe una persona con ese nombre",
            context={"nombre": persona_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.personas.create(db, tenant_id=current_user.tenant_id, obj_in=persona_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("persona_error", "No se pudo crear la persona")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("persona_error", "No se pudo crear la persona")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/{persona_id}", response_model=PersonaOut)
def read_persona(
    *,
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PersonaOut:
    persona = crud.personas.get(
        db,
        tenant_id=current_user.tenant_id,
        persona_id=persona_id,
    )
    if not persona:
        detail = error_detail(
            "persona_not_found",
            "Persona no encontrada",
            context={"persona_id": persona_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return persona


@router.put("/{persona_id}", response_model=PersonaOut)
def update_persona(
    *,
    persona_id: int,
    persona_in: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PersonaOut:
    persona = crud.personas.get(
        db,
        tenant_id=current_user.tenant_id,
        persona_id=persona_id,
    )
    if not persona:
        detail = error_detail(
            "persona_not_found",
            "Persona no encontrada",
            context={"persona_id": persona_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if persona_in.nombre and persona_in.nombre != persona.nombre:
        existente = crud.personas.get_by_nombre(
            db,
            tenant_id=current_user.tenant_id,
            nombre=persona_in.nombre,
        )
        if existente:
            detail = error_detail(
                "persona_duplicate",
                "Ya existe una persona con ese nombre",
                context={"nombre": persona_in.nombre},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.personas.update(db, db_obj=persona, obj_in=persona_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("persona_error", "No se pudo actualizar la persona")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("persona_error", "No se pudo actualizar la persona")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(
    *,
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    persona = crud.personas.get(
        db,
        tenant_id=current_user.tenant_id,
        persona_id=persona_id,
    )
    if not persona:
        detail = error_detail(
            "persona_not_found",
            "Persona no encontrada",
            context={"persona_id": persona_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    try:
        crud.personas.delete(db, db_obj=persona)
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("persona_error", "No se pudo eliminar la persona")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
