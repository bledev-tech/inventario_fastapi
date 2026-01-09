from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.producto import Producto


class Categoria(TenantMixin, Base):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("tenant_id", "nombre", name="uq_categorias_tenant_nombre"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    productos: Mapped[list["Producto"]] = relationship("Producto", back_populates="categoria")
