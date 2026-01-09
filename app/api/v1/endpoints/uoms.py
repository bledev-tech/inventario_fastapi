from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.uom import UOMCreate, UOMOut, UOMUpdate

router = APIRouter()


@router.get("/", response_model=list[UOMOut])
def read_uoms(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UOMOut]:
    return crud.uoms.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=UOMOut, status_code=status.HTTP_201_CREATED)
def create_uom(
    *,
    uom_in: UOMCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UOMOut:
    if crud.uoms.get_by_nombre(db, tenant_id=current_user.tenant_id, nombre=uom_in.nombre):
        detail = error_detail(
            "uom_duplicate_nombre",
            "Ya existe una unidad con ese nombre",
            context={"nombre": uom_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    if crud.uoms.get_by_abreviatura(
        db,
        tenant_id=current_user.tenant_id,
        abreviatura=uom_in.abreviatura,
    ):
        detail = error_detail(
            "uom_duplicate_abreviatura",
            "Ya existe una unidad con esa abreviatura",
            context={"abreviatura": uom_in.abreviatura},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.uoms.create(db, tenant_id=current_user.tenant_id, obj_in=uom_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("uom_error", "No se pudo crear la unidad de medida")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("uom_error", "No se pudo crear la unidad de medida")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/{uom_id}", response_model=UOMOut)
def read_uom(
    *,
    uom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UOMOut:
    uom = crud.uoms.get(db, tenant_id=current_user.tenant_id, uom_id=uom_id)
    if not uom:
        detail = error_detail(
            "uom_not_found",
            "Unidad de medida no encontrada",
            context={"uom_id": uom_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return uom


@router.put("/{uom_id}", response_model=UOMOut)
def update_uom(
    *,
    uom_id: int,
    uom_in: UOMUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UOMOut:
    uom = crud.uoms.get(db, tenant_id=current_user.tenant_id, uom_id=uom_id)
    if not uom:
        detail = error_detail(
            "uom_not_found",
            "Unidad de medida no encontrada",
            context={"uom_id": uom_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if uom_in.nombre and uom_in.nombre != uom.nombre:
        if crud.uoms.get_by_nombre(db, tenant_id=current_user.tenant_id, nombre=uom_in.nombre):
            detail = error_detail(
                "uom_duplicate_nombre",
                "Ya existe una unidad con ese nombre",
                context={"nombre": uom_in.nombre},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    if uom_in.abreviatura and uom_in.abreviatura != uom.abreviatura:
        if crud.uoms.get_by_abreviatura(
            db,
            tenant_id=current_user.tenant_id,
            abreviatura=uom_in.abreviatura,
        ):
            detail = error_detail(
                "uom_duplicate_abreviatura",
                "Ya existe una unidad con esa abreviatura",
                context={"abreviatura": uom_in.abreviatura},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.uoms.update(db, db_obj=uom, obj_in=uom_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("uom_error", "No se pudo actualizar la unidad de medida")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("uom_error", "No se pudo actualizar la unidad de medida")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.delete("/{uom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_uom(
    *,
    uom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    uom = crud.uoms.get(db, tenant_id=current_user.tenant_id, uom_id=uom_id)
    if not uom:
        detail = error_detail(
            "uom_not_found",
            "Unidad de medida no encontrada",
            context={"uom_id": uom_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    try:
        crud.uoms.delete(db, db_obj=uom)
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("uom_error", "No se pudo eliminar la unidad de medida")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
