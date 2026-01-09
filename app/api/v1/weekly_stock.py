"""
Endpoints para vistas de stock semanal
"""
from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.weekly_stock import WeeklyStockResponse
from app.services.weekly_stock_service import get_weekly_stock

router = APIRouter(prefix="/weekly-stock", tags=["Weekly Stock"])


@router.get("", response_model=WeeklyStockResponse)
def get_weekly_stock_view(
    week_start: date = Query(..., description="Fecha de inicio de semana (lunes) YYYY-MM-DD"),
    categories: str | None = Query(None, description="IDs de categorías separados por coma (ej: 1,2,3)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene el reporte de stock semanal por categorías.
    
    - **week_start**: Fecha del lunes de la semana a consultar (YYYY-MM-DD)
    - **categories**: IDs de categorías separados por coma. Si no se especifica, trae todas.
    """
    # Parsear categorías
    category_ids = None
    if categories:
        try:
            category_ids = [int(x.strip()) for x in categories.split(",") if x.strip()]
        except ValueError:
            category_ids = None
    
    result = get_weekly_stock(
        db,
        tenant_id=current_user.tenant_id,
        week_start=week_start,
        category_ids=category_ids
    )
    
    return result


@router.get("/csv")
def export_weekly_stock_csv(
    week_start: date = Query(..., description="Fecha de inicio de semana (lunes) YYYY-MM-DD"),
    categories: str | None = Query(None, description="IDs de categorías separados por coma"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Exporta el reporte de stock semanal a CSV.
    """
    # Parsear categorías
    category_ids = None
    if categories:
        try:
            category_ids = [int(x.strip()) for x in categories.split(",") if x.strip()]
        except ValueError:
            category_ids = None
    
    # Obtener datos
    result = get_weekly_stock(
        db,
        tenant_id=current_user.tenant_id,
        week_start=week_start,
        category_ids=category_ids
    )
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezados
    headers = [
        "Categoría",
        "Producto",
        "Marca",
        "Proveedor",
        "Stock Inicial",
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
        "Stock Final"
    ]
    writer.writerow(headers)
    
    # Datos
    for category in result.categories:
        for product in category.products:
            row = [
                category.category_name,
                product.name,
                product.brand or "",
                product.supplier or "",
                product.initial_stock,
                product.daily_movements.monday if product.daily_movements.monday is not None else "-",
                product.daily_movements.tuesday if product.daily_movements.tuesday is not None else "-",
                product.daily_movements.wednesday if product.daily_movements.wednesday is not None else "-",
                product.daily_movements.thursday if product.daily_movements.thursday is not None else "-",
                product.daily_movements.friday if product.daily_movements.friday is not None else "-",
                product.daily_movements.saturday if product.daily_movements.saturday is not None else "-",
                product.daily_movements.sunday if product.daily_movements.sunday is not None else "-",
                product.final_stock_realtime
            ]
            writer.writerow(row)
    
    # Preparar respuesta
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=stock_semanal_{week_start}.csv"
        }
    )
