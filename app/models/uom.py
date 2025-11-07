from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.producto import Producto


class UOM(Base):
    __tablename__ = "uoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    abreviatura: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    productos: Mapped[list["Producto"]] = relationship("Producto", back_populates="uom")
