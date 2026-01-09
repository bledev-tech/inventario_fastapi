from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.proveedor import ProveedorCreate, ProveedorOut, ProveedorUpdate

router = APIRouter()


@router.get("/", response_model=list[ProveedorOut])
def read_proveedores(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProveedorOut]:
    return crud.proveedores.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ProveedorOut, status_code=status.HTTP_201_CREATED)
def create_proveedor(
    *,
    proveedor_in: ProveedorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProveedorOut:
    existente = crud.proveedores.get_by_nombre(
        db,
        tenant_id=current_user.tenant_id,
        nombre=proveedor_in.nombre,
    )
    if existente:
        detail = error_detail(
            "proveedor_duplicate",
            "Ya existe un proveedor con ese nombre",
            context={"nombre": proveedor_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.proveedores.create(db, tenant_id=current_user.tenant_id, obj_in=proveedor_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("proveedor_error", "No se pudo crear el proveedor")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("proveedor_error", "No se pudo crear el proveedor")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/{proveedor_id}", response_model=ProveedorOut)
def read_proveedor(
    *,
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProveedorOut:
    proveedor = crud.proveedores.get(
        db,
        tenant_id=current_user.tenant_id,
        proveedor_id=proveedor_id,
    )
    if not proveedor:
        detail = error_detail(
            "proveedor_not_found",
            "Proveedor no encontrado",
            context={"proveedor_id": proveedor_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return proveedor


@router.put("/{proveedor_id}", response_model=ProveedorOut)
def update_proveedor(
    *,
    proveedor_id: int,
    proveedor_in: ProveedorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProveedorOut:
    proveedor = crud.proveedores.get(
        db,
        tenant_id=current_user.tenant_id,
        proveedor_id=proveedor_id,
    )
    if not proveedor:
        detail = error_detail(
            "proveedor_not_found",
            "Proveedor no encontrado",
            context={"proveedor_id": proveedor_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if proveedor_in.nombre and proveedor_in.nombre != proveedor.nombre:
        existente = crud.proveedores.get_by_nombre(
            db,
            tenant_id=current_user.tenant_id,
            nombre=proveedor_in.nombre,
        )
        if existente:
            detail = error_detail(
                "proveedor_duplicate",
                "Ya existe un proveedor con ese nombre",
                context={"nombre": proveedor_in.nombre},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.proveedores.update(db, db_obj=proveedor, obj_in=proveedor_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("proveedor_error", "No se pudo actualizar el proveedor")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("proveedor_error", "No se pudo actualizar el proveedor")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proveedor(
    *,
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    proveedor = crud.proveedores.get(
        db,
        tenant_id=current_user.tenant_id,
        proveedor_id=proveedor_id,
    )
    if not proveedor:
        detail = error_detail(
            "proveedor_not_found",
            "Proveedor no encontrado",
            context={"proveedor_id": proveedor_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    try:
        crud.proveedores.delete(db, db_obj=proveedor)
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("proveedor_error", "No se pudo eliminar el proveedor")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
