from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, condecimal, model_validator

from app.models.movimiento import TipoMovimiento

CantidadDecimal = condecimal(gt=0, max_digits=14, decimal_places=3)


class MovimientoBase(BaseModel):
    producto_id: int = Field(..., gt=0)
    tipo: TipoMovimiento
    from_locacion_id: int | None = Field(default=None, gt=0)
    to_locacion_id: int | None = Field(default=None, gt=0)
    persona_id: int | None = Field(default=None, gt=0)
    cantidad: CantidadDecimal
    nota: str | None = None

    @model_validator(mode="after")
    def validar_reglas_de_movimiento(self) -> "MovimientoBase":
        tipo = self.tipo
        from_id = self.from_locacion_id
        to_id = self.to_locacion_id

        if tipo is TipoMovimiento.ingreso:
            if to_id is None:
                raise ValueError("Los ingresos requieren locacion destino")
            if from_id is not None:
                raise ValueError("Los ingresos no aceptan locacion origen")
        elif tipo is TipoMovimiento.traspaso:
            if from_id is None or to_id is None:
                raise ValueError("Los traspasos requieren locacion origen y destino")
            if from_id == to_id:
                raise ValueError("Los traspasos deben usar locaciones distintas")
        elif tipo is TipoMovimiento.uso:
            if from_id is None:
                raise ValueError("Los usos requieren locacion origen")
            if to_id is not None:
                raise ValueError("Los usos no aceptan locacion destino")
        elif tipo is TipoMovimiento.ajuste:
            if from_id is None and to_id is None:
                raise ValueError("Los ajustes requieren al menos una locacion")

        return self


class MovimientoCreate(MovimientoBase):
    pass


class MovimientoOut(MovimientoBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True
