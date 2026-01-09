from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.movimiento import TipoMovimiento
from app.models.user import User
from app.schemas.movimiento import MovimientoCreate, MovimientoOut

router = APIRouter()


@router.get("/", response_model=list[MovimientoOut])
def read_movimientos(
    *,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    producto_id: int | None = Query(default=None, gt=0),
    locacion_id: int | None = Query(default=None, gt=0),
    tipo: TipoMovimiento | None = Query(default=None),
    persona_id: int | None = Query(default=None, gt=0),
    proveedor_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MovimientoOut]:
    if producto_id is not None:
        producto = crud.productos.get(
            db,
            tenant_id=current_user.tenant_id,
            producto_id=producto_id,
        )
        if not producto:
            detail = error_detail(
                "producto_not_found",
                "Producto no encontrado",
                context={"producto_id": producto_id},
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if locacion_id is not None:
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

    if persona_id is not None:
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

    if proveedor_id is not None:
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

    return crud.movimientos.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        producto_id=producto_id,
        locacion_id=locacion_id,
        tipo=tipo,
        persona_id=persona_id,
        proveedor_id=proveedor_id,
    )


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def create_movimiento(
    *,
    movimiento_in: MovimientoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MovimientoOut:
    producto = crud.productos.get(
        db,
        tenant_id=current_user.tenant_id,
        producto_id=movimiento_in.producto_id,
    )
    if not producto:
        detail = error_detail(
            "producto_not_found",
            "Producto no encontrado",
            context={"producto_id": movimiento_in.producto_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if movimiento_in.from_locacion_id is not None:
        locacion = crud.locaciones.get(
            db,
            tenant_id=current_user.tenant_id,
            locacion_id=movimiento_in.from_locacion_id,
        )
        if not locacion:
            detail = error_detail(
                "locacion_not_found",
                "Locacion origen no encontrada",
                context={"locacion_id": movimiento_in.from_locacion_id},
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if movimiento_in.to_locacion_id is not None:
        locacion = crud.locaciones.get(
            db,
            tenant_id=current_user.tenant_id,
            locacion_id=movimiento_in.to_locacion_id,
        )
        if not locacion:
            detail = error_detail(
                "locacion_not_found",
                "Locacion destino no encontrada",
                context={"locacion_id": movimiento_in.to_locacion_id},
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if movimiento_in.persona_id is not None:
        persona = crud.personas.get(
            db,
            tenant_id=current_user.tenant_id,
            persona_id=movimiento_in.persona_id,
        )
        if not persona:
            detail = error_detail(
                "persona_not_found",
                "Persona no encontrada",
                context={"persona_id": movimiento_in.persona_id},
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if movimiento_in.proveedor_id is not None:
        proveedor = crud.proveedores.get(
            db,
            tenant_id=current_user.tenant_id,
            proveedor_id=movimiento_in.proveedor_id,
        )
        if not proveedor:
            detail = error_detail(
                "proveedor_not_found",
                "Proveedor no encontrado",
                context={"proveedor_id": movimiento_in.proveedor_id},
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    try:
        return crud.movimientos.create(db, tenant_id=current_user.tenant_id, obj_in=movimiento_in)
    except (IntegrityError, DataError) as exc:
        db.rollback()
        origin = getattr(exc, "orig", exc)
        detail = error_detail(
            "movimiento_invalido",
            "La base de datos rechazo el movimiento",
            context={"motivo": str(origin)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("movimiento_error", "No se pudo crear el movimiento")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/producto/{producto_id}", response_model=list[MovimientoOut])
def read_movimientos_por_producto(
    *,
    producto_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MovimientoOut]:
    producto = crud.productos.get(
        db,
        tenant_id=current_user.tenant_id,
        producto_id=producto_id,
    )
    if not producto:
        detail = error_detail(
            "producto_not_found",
            "Producto no encontrado",
            context={"producto_id": producto_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return crud.movimientos.get_multi_by_producto(
        db,
        tenant_id=current_user.tenant_id,
        producto_id=producto_id,
        skip=skip,
        limit=limit,
    )


@router.get("/dia", response_model=list[MovimientoOut])
def read_movimientos_por_dia(
    *,
    fecha: date | None = Query(
        default=None,
        description="Fecha (UTC) para filtrar los movimientos. Si se omite se usa el dia actual.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MovimientoOut]:
    target_date = fecha or date.today()
    return crud.movimientos.get_por_dia(
        db,
        tenant_id=current_user.tenant_id,
        fecha=target_date,
    )
