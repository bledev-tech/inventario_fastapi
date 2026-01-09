from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.marca import MarcaCreate, MarcaOut, MarcaUpdate

router = APIRouter()


@router.get("/", response_model=list[MarcaOut])
def read_marcas(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MarcaOut]:
    return crud.marcas.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=MarcaOut, status_code=status.HTTP_201_CREATED)
def create_marca(
    *,
    marca_in: MarcaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarcaOut:
    existente = crud.marcas.get_by_nombre(
        db,
        tenant_id=current_user.tenant_id,
        nombre=marca_in.nombre,
    )
    if existente:
        detail = error_detail(
            "marca_duplicate",
            "Ya existe una marca con ese nombre",
            context={"nombre": marca_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.marcas.create(db, tenant_id=current_user.tenant_id, obj_in=marca_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("marca_error", "No se pudo crear la marca")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("marca_error", "No se pudo crear la marca")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/{marca_id}", response_model=MarcaOut)
def read_marca(
    *,
    marca_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarcaOut:
    marca = crud.marcas.get(
        db,
        tenant_id=current_user.tenant_id,
        marca_id=marca_id,
    )
    if not marca:
        detail = error_detail(
            "marca_not_found",
            "Marca no encontrada",
            context={"marca_id": marca_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return marca


@router.put("/{marca_id}", response_model=MarcaOut)
def update_marca(
    *,
    marca_id: int,
    marca_in: MarcaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarcaOut:
    marca = crud.marcas.get(
        db,
        tenant_id=current_user.tenant_id,
        marca_id=marca_id,
    )
    if not marca:
        detail = error_detail(
            "marca_not_found",
            "Marca no encontrada",
            context={"marca_id": marca_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if marca_in.nombre and marca_in.nombre != marca.nombre:
        existente = crud.marcas.get_by_nombre(
            db,
            tenant_id=current_user.tenant_id,
            nombre=marca_in.nombre,
        )
        if existente:
            detail = error_detail(
                "marca_duplicate",
                "Ya existe una marca con ese nombre",
                context={"nombre": marca_in.nombre},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.marcas.update(db, db_obj=marca, obj_in=marca_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("marca_error", "No se pudo actualizar la marca")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("marca_error", "No se pudo actualizar la marca")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.delete("/{marca_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_marca(
    *,
    marca_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    marca = crud.marcas.get(
        db,
        tenant_id=current_user.tenant_id,
        marca_id=marca_id,
    )
    if not marca:
        detail = error_detail(
            "marca_not_found",
            "Marca no encontrada",
            context={"marca_id": marca_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    try:
        crud.marcas.delete(db, db_obj=marca)
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("marca_error", "No se pudo eliminar la marca")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
