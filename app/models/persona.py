from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.movimiento import Movimiento


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    movimientos: Mapped[list["Movimiento"]] = relationship("Movimiento", back_populates="persona")

    def __repr__(self) -> str:
        return f"Persona(id={self.id!r}, nombre={self.nombre!r}, activa={self.activa!r})"
