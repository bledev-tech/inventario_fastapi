from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum as PgEnum, ForeignKey, Numeric, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.locacion import Locacion
    from app.models.persona import Persona
    from app.models.producto import Producto
    from app.models.proveedor import Proveedor


class TipoMovimiento(str, Enum):
    ingreso = "ingreso"
    traspaso = "traspaso"
    uso = "uso"
    ajuste = "ajuste"


class Movimiento(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    tipo: Mapped[TipoMovimiento] = mapped_column(
        PgEnum(TipoMovimiento, name="tipo_movimiento", create_type=False), nullable=False, 
    )
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    from_locacion_id: Mapped[int | None] = mapped_column(ForeignKey("locaciones.id"), nullable=True)
    to_locacion_id: Mapped[int | None] = mapped_column(ForeignKey("locaciones.id"), nullable=True)
    persona_id: Mapped[int | None] = mapped_column(ForeignKey("personas.id"), nullable=True)
    proveedor_id: Mapped[int | None] = mapped_column(ForeignKey("proveedores.id"), nullable=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    nota: Mapped[str | None] = mapped_column(Text, nullable=True)

    producto: Mapped["Producto"] = relationship("Producto", back_populates="movimientos")
    from_locacion: Mapped["Locacion | None"] = relationship(
        "Locacion", foreign_keys=[from_locacion_id], back_populates="movimientos_origen"
    )
    to_locacion: Mapped["Locacion | None"] = relationship(
        "Locacion", foreign_keys=[to_locacion_id], back_populates="movimientos_destino"
    )
    persona: Mapped["Persona | None"] = relationship("Persona", back_populates="movimientos")
    proveedor: Mapped["Proveedor | None"] = relationship("Proveedor", back_populates="movimientos")
