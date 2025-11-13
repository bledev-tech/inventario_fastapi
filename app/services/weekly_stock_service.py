"""
Servicio para calcular stock semanal por categorías
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, case
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Producto,
    Categoria,
    Marca,
    Movimiento,
)
from app.schemas.weekly_stock import (
    WeeklyStockResponse,
    WeeklyCategory,
    WeeklyProduct,
    DailyMovements,
)


def _get_monday(d: date) -> date:
    """Obtiene el lunes de la semana dada"""
    return d - timedelta(days=d.weekday())


def _get_stock_at_date(db: Session, producto_id: int, until_date: date) -> float:
    """
    Calcula el stock de un producto hasta una fecha dada.
    INGRESO suma (+), USO resta (-), TRASPASO no afecta stock total.
    """
    result = db.query(
        func.coalesce(
            func.sum(
                case(
                    (Movimiento.tipo == 'ingreso', Movimiento.cantidad),
                    (Movimiento.tipo == 'uso', -Movimiento.cantidad),
                    else_=0
                )
            ),
            0
        )
    ).filter(
        Movimiento.producto_id == producto_id,
        func.date(Movimiento.fecha) <= until_date
    ).scalar()
    
    return float(result or 0)


def _get_current_stock(db: Session, producto_id: int) -> float:
    """
    Obtiene el stock actual real del producto calculando:
    INGRESO suma (+), USO resta (-), TRASPASO no afecta stock total.
    """
    result = db.query(
        func.coalesce(
            func.sum(
                case(
                    (Movimiento.tipo == 'ingreso', Movimiento.cantidad),
                    (Movimiento.tipo == 'uso', -Movimiento.cantidad),
                    else_=0
                )
            ),
            0
        )
    ).filter(
        Movimiento.producto_id == producto_id
    ).scalar()
    
    return float(result or 0)


def get_weekly_stock(
    db: Session,
    *,
    week_start: date,
    category_ids: list[int] | None = None
) -> WeeklyStockResponse:
    """
    Obtiene el reporte semanal de stock por categorías.
    
    Args:
        db: Sesión de base de datos
        week_start: Fecha de inicio de semana (debe ser lunes)
        category_ids: Lista de IDs de categorías a filtrar (None = todas)
    
    Returns:
        WeeklyStockResponse con datos de stock semanal
    """
    # Asegurar que week_start sea lunes
    monday = _get_monday(week_start)
    
    # Calcular fechas de la semana
    week_dates = {
        'monday': monday,
        'tuesday': monday + timedelta(days=1),
        'wednesday': monday + timedelta(days=2),
        'thursday': monday + timedelta(days=3),
        'friday': monday + timedelta(days=4),
        'saturday': monday + timedelta(days=5),
        'sunday': monday + timedelta(days=6),
    }
    
    # Fecha límite (domingo)
    week_end = monday + timedelta(days=6)
    
    # Fecha del día anterior al lunes (para stock inicial)
    prev_day = monday - timedelta(days=1)
    
    # Query base de productos
    query = db.query(Producto).filter(Producto.activo == True)
    
    # Filtrar por categorías si se especifican
    if category_ids:
        query = query.filter(Producto.categoria_id.in_(category_ids))
    
    # Obtener productos con sus relaciones
    productos = query.options(
        joinedload(Producto.categoria),
        joinedload(Producto.marca)
    ).all()
    
    # Agrupar productos por categoría
    categories_map: dict[int, list[Producto]] = {}
    for producto in productos:
        cat_id = producto.categoria_id
        if cat_id not in categories_map:
            categories_map[cat_id] = []
        categories_map[cat_id].append(producto)
    
    # Procesar cada categoría
    categories_result = []
    
    for cat_id, cat_productos in categories_map.items():
        # Obtener info de categoría
        categoria = cat_productos[0].categoria
        
        weekly_products = []
        
        for producto in cat_productos:
            # Calcular stock inicial (al final del día anterior al lunes)
            initial_stock = _get_stock_at_date(db, producto.id, prev_day)
            
            # Calcular movimientos diarios
            daily_movements_data = {}
            
            for day_name, day_date in week_dates.items():
                # Si la fecha es futura, no calcular
                if day_date > date.today():
                    daily_movements_data[day_name] = None
                else:
                    # Calcular movimientos del día: INGRESO suma, USO resta
                    movement_sum = db.query(
                        func.coalesce(
                            func.sum(
                                case(
                                    (Movimiento.tipo == 'ingreso', Movimiento.cantidad),
                                    (Movimiento.tipo == 'uso', -Movimiento.cantidad),
                                    else_=0
                                )
                            ),
                            0
                        )
                    ).filter(
                        Movimiento.producto_id == producto.id,
                        func.date(Movimiento.fecha) == day_date
                    ).scalar()
                    
                    daily_movements_data[day_name] = float(movement_sum or 0)
            
            # Obtener stock actual real (fuente de verdad)
            final_stock_realtime = _get_current_stock(db, producto.id)
            
            # Crear objeto WeeklyProduct
            weekly_product = WeeklyProduct(
                id=producto.id,
                name=producto.nombre,
                brand=producto.marca.nombre if producto.marca else None,
                supplier=None,  # No existe relación proveedor en Producto
                initial_stock=initial_stock,
                daily_movements=DailyMovements(**daily_movements_data),
                final_stock_realtime=final_stock_realtime
            )
            
            weekly_products.append(weekly_product)
        
        # Crear objeto WeeklyCategory
        weekly_category = WeeklyCategory(
            category_id=cat_id,
            category_name=categoria.nombre,
            products=weekly_products
        )
        
        categories_result.append(weekly_category)
    
    return WeeklyStockResponse(
        week_start=monday.isoformat(),
        categories=categories_result
    )
