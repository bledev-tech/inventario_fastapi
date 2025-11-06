from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_db
from app.api.utils import error_detail
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter()


@router.get("/", response_model=list[ProductoOut])
def read_productos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ProductoOut]:
    return crud.productos.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def create_producto(*, producto_in: ProductoCreate, db: Session = Depends(get_db)) -> ProductoOut:
    if producto_in.sku:
        existente = crud.productos.get_by_sku(db, producto_in.sku)
        if existente:
            detail = error_detail(
                "producto_sku_duplicate",
                "SKU ya registrado",
                context={"sku": producto_in.sku},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.productos.create(db, obj_in=producto_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("producto_error", "No se pudo crear el producto")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("producto_error", "No se pudo crear el producto")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/{producto_id}", response_model=ProductoOut)
def read_producto(*, producto_id: int, db: Session = Depends(get_db)) -> ProductoOut:
    producto = crud.productos.get(db, producto_id)
    if not producto:
        detail = error_detail(
            "producto_not_found",
            "Producto no encontrado",
            context={"producto_id": producto_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def update_producto(*, producto_id: int, producto_in: ProductoUpdate, db: Session = Depends(get_db)) -> ProductoOut:
    producto = crud.productos.get(db, producto_id)
    if not producto:
        detail = error_detail(
            "producto_not_found",
            "Producto no encontrado",
            context={"producto_id": producto_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if producto_in.sku and producto_in.sku != producto.sku:
        existente = crud.productos.get_by_sku(db, producto_in.sku)
        if existente:
            detail = error_detail(
                "producto_sku_duplicate",
                "SKU ya registrado",
                context={"sku": producto_in.sku},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.productos.update(db, db_obj=producto, obj_in=producto_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("producto_error", "No se pudo actualizar el producto")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("producto_error", "No se pudo actualizar el producto")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(*, producto_id: int, db: Session = Depends(get_db)) -> Response:
    producto = crud.productos.get(db, producto_id)
    if not producto:
        detail = error_detail(
            "producto_not_found",
            "Producto no encontrado",
            context={"producto_id": producto_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    try:
        crud.productos.delete(db, db_obj=producto)
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("producto_error", "No se pudo eliminar el producto")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
