from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.locacion import LocacionCreate, LocacionOut, LocacionUpdate

router = APIRouter()


@router.get("/", response_model=list[LocacionOut])
def read_locaciones(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LocacionOut]:
    return crud.locaciones.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=LocacionOut, status_code=status.HTTP_201_CREATED)
def create_locacion(
    *,
    locacion_in: LocacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LocacionOut:
    try:
        return crud.locaciones.create(db, tenant_id=current_user.tenant_id, obj_in=locacion_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail(
            "locacion_duplicate",
            "Ya existe una locacion con ese nombre",
            context={"nombre": locacion_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("locacion_error", "No se pudo crear la locacion")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.put("/{locacion_id}", response_model=LocacionOut)
def update_locacion(
    *,
    locacion_id: int,
    locacion_in: LocacionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LocacionOut:
    locacion = crud.locaciones.get(
        db,
        tenant_id=current_user.tenant_id,
        locacion_id=locacion_id,
    )
    if not locacion:
        detail = error_detail(
            "locacion_not_found",
            "Locacion no encontrada",
            context={"locacion_id": locacion_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    try:
        return crud.locaciones.update(db, db_obj=locacion, obj_in=locacion_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail(
            "locacion_duplicate",
            "Ya existe una locacion con ese nombre",
            context={"nombre": locacion_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("locacion_error", "No se pudo actualizar la locacion")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
