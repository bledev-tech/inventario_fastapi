from fastapi import APIRouter

from app.api.v1.endpoints import (
    categorias,
    locaciones,
    marcas,
    movimientos,
    personas,
    productos,
    proveedores,
    stock,
    uoms,
)

api_router = APIRouter()
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(marcas.router, prefix="/marcas", tags=["marcas"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["categorias"])
api_router.include_router(uoms.router, prefix="/uoms", tags=["unidades"])
api_router.include_router(locaciones.router, prefix="/locaciones", tags=["locaciones"])
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(proveedores.router, prefix="/proveedores", tags=["proveedores"])
api_router.include_router(movimientos.router, prefix="/movimientos", tags=["movimientos"])
api_router.include_router(stock.router, prefix="/stock", tags=["stock"])
