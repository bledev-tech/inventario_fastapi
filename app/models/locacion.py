from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.movimiento import Movimiento


class Locacion(TenantMixin, Base):
    __tablename__ = "locaciones"
    __table_args__ = (
        UniqueConstraint("tenant_id", "nombre", name="uq_locaciones_tenant_nombre"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    movimientos_origen: Mapped[list["Movimiento"]] = relationship(
        "Movimiento",
        back_populates="from_locacion",
        foreign_keys="Movimiento.from_locacion_id",
    )
    movimientos_destino: Mapped[list["Movimiento"]] = relationship(
        "Movimiento",
        back_populates="to_locacion",
        foreign_keys="Movimiento.to_locacion_id",
    )
