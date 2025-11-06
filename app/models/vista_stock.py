from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class VistaStockActual(Base):
    __tablename__ = "vista_stock_actual"
    __table_args__ = {"info": {"is_view": True}}

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), primary_key=True)
    locacion_id: Mapped[int] = mapped_column(ForeignKey("locaciones.id"), primary_key=True)
    stock: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
