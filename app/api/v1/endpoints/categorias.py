from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.api.utils import error_detail
from app.models.user import User
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter()


@router.get("/", response_model=list[CategoriaOut])
def read_categorias(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CategoriaOut]:
    return crud.categorias.get_multi(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def create_categoria(
    *,
    categoria_in: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoriaOut:
    existente = crud.categorias.get_by_nombre(
        db,
        tenant_id=current_user.tenant_id,
        nombre=categoria_in.nombre,
    )
    if existente:
        detail = error_detail(
            "categoria_duplicate",
            "Ya existe una categoria con ese nombre",
            context={"nombre": categoria_in.nombre},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.categorias.create(db, tenant_id=current_user.tenant_id, obj_in=categoria_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("categoria_error", "No se pudo crear la categoria")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("categoria_error", "No se pudo crear la categoria")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/{categoria_id}", response_model=CategoriaOut)
def read_categoria(
    *,
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoriaOut:
    categoria = crud.categorias.get(
        db,
        tenant_id=current_user.tenant_id,
        categoria_id=categoria_id,
    )
    if not categoria:
        detail = error_detail(
            "categoria_not_found",
            "Categoria no encontrada",
            context={"categoria_id": categoria_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaOut)
def update_categoria(
    *,
    categoria_id: int,
    categoria_in: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoriaOut:
    categoria = crud.categorias.get(
        db,
        tenant_id=current_user.tenant_id,
        categoria_id=categoria_id,
    )
    if not categoria:
        detail = error_detail(
            "categoria_not_found",
            "Categoria no encontrada",
            context={"categoria_id": categoria_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if categoria_in.nombre and categoria_in.nombre != categoria.nombre:
        existente = crud.categorias.get_by_nombre(
            db,
            tenant_id=current_user.tenant_id,
            nombre=categoria_in.nombre,
        )
        if existente:
            detail = error_detail(
                "categoria_duplicate",
                "Ya existe una categoria con ese nombre",
                context={"nombre": categoria_in.nombre},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    try:
        return crud.categorias.update(db, db_obj=categoria, obj_in=categoria_in)
    except IntegrityError as exc:
        db.rollback()
        detail = error_detail("categoria_error", "No se pudo actualizar la categoria")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("categoria_error", "No se pudo actualizar la categoria")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    *,
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    categoria = crud.categorias.get(
        db,
        tenant_id=current_user.tenant_id,
        categoria_id=categoria_id,
    )
    if not categoria:
        detail = error_detail(
            "categoria_not_found",
            "Categoria no encontrada",
            context={"categoria_id": categoria_id},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    try:
        crud.categorias.delete(db, db_obj=categoria)
    except SQLAlchemyError as exc:
        db.rollback()
        detail = error_detail("categoria_error", "No se pudo eliminar la categoria")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
