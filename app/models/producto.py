from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.marca import Marca
    from app.models.movimiento import Movimiento


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    marca_id: Mapped[int | None] = mapped_column(
        ForeignKey("marcas.id", ondelete="SET NULL"), nullable=True
    )
    categoria_id: Mapped[int | None] = mapped_column(
        ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True
    )

    movimientos: Mapped[list["Movimiento"]] = relationship(
        "Movimiento",
        back_populates="producto",
    )
    marca: Mapped["Marca | None"] = relationship("Marca", back_populates="productos")
    categoria: Mapped["Categoria | None"] = relationship("Categoria", back_populates="productos")
