from fastapi import APIRouter

from app.api.v1.endpoints import locaciones, movimientos, personas, productos, stock

api_router = APIRouter()
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(locaciones.router, prefix="/locaciones", tags=["locaciones"])
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(movimientos.router, prefix="/movimientos", tags=["movimientos"])
api_router.include_router(stock.router, prefix="/stock", tags=["stock"])
