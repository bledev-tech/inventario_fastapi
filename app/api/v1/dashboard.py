from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.movimiento import TipoMovimiento
from app.models.user import User
from app.schemas.dashboard import (
    AdjustmentsMonitorResponse,
    DashboardSummaryResponse,
    RecentMovementsResponse,
    StockByLocationResponse,
    TopCategoriesResponse,
    TopUsedProductsResponse,
)
from app.services.dashboard_service import (
    get_adjustments_monitor,
    get_dashboard_summary,
    get_recent_movements,
    get_stock_by_location,
    get_top_categories,
    get_top_used_products,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="KPIs recientes del inventario",
    description="Devuelve métricas clave de los últimos 7 y 30 días para alimentar el dashboard.",
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummaryResponse:
    return get_dashboard_summary(db, tenant_id=current_user.tenant_id)


@router.get(
    "/recent-movements",
    response_model=RecentMovementsResponse,
    summary="Últimos movimientos",
    description="Lista los movimientos más recientes con contexto listo para UI, ordenados de más nuevo a más antiguo.",
)
def recent_movements(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200, description="Cantidad de registros a devolver."),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginar los registros."),
    tipo: TipoMovimiento | None = Query(
        default=None,
        description="Filtra por tipo de movimiento. Opcional y listo para ajustes posteriores.",
    ),
    locacion_id: int | None = Query(
        default=None,
        gt=0,
        description="Filtra los movimientos donde participe la locación (origen o destino).",
    ),
    producto_id: int | None = Query(
        default=None,
        gt=0,
        description="Filtra por producto específico.",
    ),
) -> RecentMovementsResponse:
    return get_recent_movements(
        db,
        tenant_id=current_user.tenant_id,
        limit=limit,
        offset=offset,
        tipo=tipo,
        locacion_id=locacion_id,
        producto_id=producto_id,
    )


@router.get(
    "/stock-by-location",
    response_model=StockByLocationResponse,
    summary="Stock agregado por locación",
    description="Resume la vista de stock actual agrupando por locación para mostrar la distribución del inventario.",
)
def stock_by_location(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StockByLocationResponse:
    return get_stock_by_location(db, tenant_id=current_user.tenant_id)


@router.get(
    "/top-used-products",
    response_model=TopUsedProductsResponse,
    summary="Top productos consumidos",
    description="Entrega los productos con mayor uso en el rango de días indicado para identificar tendencias de consumo.",
)
def top_used_products(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Rango de días hacia atrás a considerar."),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima de productos en la respuesta."),
) -> TopUsedProductsResponse:
    return get_top_used_products(db, tenant_id=current_user.tenant_id, days=days, limit=limit)


@router.get(
    "/top-categories",
    response_model=TopCategoriesResponse,
    summary="Top categorias con mas movimiento",
    description="Agrupa movimientos por categoria de producto para detectar las que mueven mayor volumen en el rango indicado.",
)
def top_categories(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Rango de dias hacia atras a considerar."),
    limit: int = Query(10, ge=1, le=100, description="Cantidad maxima de categorias en la respuesta."),
) -> TopCategoriesResponse:
    return get_top_categories(db, tenant_id=current_user.tenant_id, days=days, limit=limit)


@router.get(
    "/adjustments-monitor",
    response_model=AdjustmentsMonitorResponse,
    summary="Monitor de ajustes",
    description="Controla la actividad de ajustes recientes, incluyendo totales y los actores más frecuentes.",
)
def adjustments_monitor(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Rango de días a analizar."),
    top: int = Query(3, ge=1, le=20, description="Cantidad de productos y locaciones destacados."),
) -> AdjustmentsMonitorResponse:
    return get_adjustments_monitor(db, tenant_id=current_user.tenant_id, days=days, top=top)
