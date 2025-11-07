-- Tipos
CREATE TYPE tipo_movimiento AS ENUM ('ingreso', 'traspaso', 'uso', 'ajuste');

-- Unidades de medida
CREATE TABLE uoms (
  id            SERIAL PRIMARY KEY,
  nombre        TEXT NOT NULL UNIQUE,
  abreviatura   TEXT NOT NULL UNIQUE,
  descripcion   TEXT,
  activa        BOOLEAN NOT NULL DEFAULT TRUE
);

-- Catalogos auxiliares
CREATE TABLE categorias (
  id      SERIAL PRIMARY KEY,
  nombre  TEXT NOT NULL UNIQUE,
  activa  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE marcas (
  id      SERIAL PRIMARY KEY,
  nombre  TEXT NOT NULL UNIQUE,
  activa  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE proveedores (
  id      SERIAL PRIMARY KEY,
  nombre  TEXT NOT NULL UNIQUE,
  activa  BOOLEAN NOT NULL DEFAULT TRUE
);

-- Catalogo de productos
CREATE TABLE productos (
  id            SERIAL PRIMARY KEY,
  sku           TEXT UNIQUE,
  nombre        TEXT NOT NULL,
  activo        BOOLEAN NOT NULL DEFAULT TRUE,
  uom_id        INTEGER NOT NULL REFERENCES uoms(id),
  marca_id      INTEGER REFERENCES marcas(id) ON DELETE SET NULL,
  categoria_id  INTEGER REFERENCES categorias(id) ON DELETE SET NULL
);

-- Zonas/Bodegas/Locaciones
CREATE TABLE locaciones (
  id      SERIAL PRIMARY KEY,
  nombre  TEXT NOT NULL UNIQUE,
  activa  BOOLEAN NOT NULL DEFAULT TRUE
);

-- Personas responsables de movimientos
CREATE TABLE personas (
  id      SERIAL PRIMARY KEY,
  nombre  TEXT NOT NULL UNIQUE,
  activa  BOOLEAN NOT NULL DEFAULT TRUE
);

-- Movimientos de inventario (Kardex simplificado)
CREATE TABLE movimientos (
  id                 BIGSERIAL PRIMARY KEY,
  fecha              TIMESTAMPTZ NOT NULL DEFAULT now(),
  tipo               tipo_movimiento NOT NULL,
  producto_id        INTEGER NOT NULL REFERENCES productos(id),
  from_locacion_id   INTEGER REFERENCES locaciones(id),
  to_locacion_id     INTEGER REFERENCES locaciones(id),
  persona_id         INTEGER REFERENCES personas(id),
  proveedor_id       INTEGER REFERENCES proveedores(id),
  cantidad           NUMERIC(14,3) NOT NULL CHECK (cantidad > 0),
  nota               TEXT
);

ALTER TABLE movimientos ADD CONSTRAINT chk_mov_ingreso
  CHECK (
    (tipo <> 'ingreso')
    OR (from_locacion_id IS NULL AND to_locacion_id IS NOT NULL)
  );

ALTER TABLE movimientos ADD CONSTRAINT chk_mov_traspaso
  CHECK (
    (tipo <> 'traspaso')
    OR (from_locacion_id IS NOT NULL AND to_locacion_id IS NOT NULL AND from_locacion_id <> to_locacion_id)
  );

ALTER TABLE movimientos ADD CONSTRAINT chk_mov_uso
  CHECK (
    (tipo <> 'uso')
    OR (from_locacion_id IS NOT NULL AND to_locacion_id IS NULL)
  );

CREATE INDEX idx_movimientos_producto_fecha ON movimientos (producto_id, fecha);
CREATE INDEX idx_movimientos_from ON movimientos (from_locacion_id);
CREATE INDEX idx_movimientos_to   ON movimientos (to_locacion_id);
CREATE INDEX idx_movimientos_persona ON movimientos (persona_id);
CREATE INDEX idx_movimientos_proveedor ON movimientos (proveedor_id);
CREATE INDEX idx_productos_uom ON productos (uom_id);

CREATE VIEW vista_stock_actual AS
SELECT
  p.id  AS producto_id,
  l.id  AS locacion_id,
  COALESCE(SUM(
    CASE
      WHEN m.to_locacion_id = l.id THEN m.cantidad
      WHEN m.from_locacion_id = l.id THEN -m.cantidad
      ELSE 0
    END
  ), 0)::NUMERIC(14,3) AS stock
FROM productos p
CROSS JOIN locaciones l
LEFT JOIN movimientos m
  ON m.producto_id = p.id
GROUP BY p.id, l.id;

CREATE OR REPLACE FUNCTION fn_evitar_stock_negativo() RETURNS trigger AS $$
DECLARE
  stock_actual NUMERIC(14,3);
BEGIN
  IF (NEW.tipo IN ('uso','traspaso')) AND NEW.from_locacion_id IS NOT NULL THEN
    SELECT COALESCE(v.stock,0) INTO stock_actual
    FROM vista_stock_actual v
    WHERE v.producto_id = NEW.producto_id
      AND v.locacion_id = NEW.from_locacion_id;

    IF stock_actual < NEW.cantidad THEN
      RAISE EXCEPTION 'Stock insuficiente en locacion origen (%. Disponible: %, Intentado: %)',
        NEW.from_locacion_id, stock_actual, NEW.cantidad;
    END IF;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_evitar_stock_negativo
BEFORE INSERT ON movimientos
FOR EACH ROW
EXECUTE FUNCTION fn_evitar_stock_negativo();
