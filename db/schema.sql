-- Tipos
CREATE TYPE tipo_movimiento AS ENUM ('ingreso', 'traspaso', 'uso', 'ajuste');

-- Tenants y usuarios
CREATE TABLE tenants (
  id          SERIAL PRIMARY KEY,
  name        TEXT NOT NULL,
  slug        TEXT NOT NULL,
  is_active   BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_tenants_slug UNIQUE (slug)
);

CREATE TABLE users (
  id              SERIAL PRIMARY KEY,
  email           TEXT NOT NULL UNIQUE,
  full_name       TEXT,
  hashed_password TEXT NOT NULL,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  is_superuser    BOOLEAN NOT NULL DEFAULT FALSE,
  tenant_id       INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Unidades de medida
CREATE TABLE uoms (
  id          SERIAL PRIMARY KEY,
  tenant_id   INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre      TEXT NOT NULL,
  abreviatura TEXT NOT NULL,
  descripcion TEXT,
  activa      BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_uoms_tenant_nombre UNIQUE (tenant_id, nombre),
  CONSTRAINT uq_uoms_tenant_abreviatura UNIQUE (tenant_id, abreviatura)
);

-- Catalogos auxiliares
CREATE TABLE categorias (
  id        SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre    TEXT NOT NULL,
  activa    BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_categorias_tenant_nombre UNIQUE (tenant_id, nombre)
);

CREATE TABLE marcas (
  id        SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre    TEXT NOT NULL,
  activa    BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_marcas_tenant_nombre UNIQUE (tenant_id, nombre)
);

CREATE TABLE proveedores (
  id        SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre    TEXT NOT NULL,
  activa    BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_proveedores_tenant_nombre UNIQUE (tenant_id, nombre)
);

-- Zonas/Bodegas/Locaciones
CREATE TABLE locaciones (
  id        SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre    TEXT NOT NULL,
  activa    BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_locaciones_tenant_nombre UNIQUE (tenant_id, nombre)
);

-- Personas responsables de movimientos
CREATE TABLE personas (
  id        SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  nombre    TEXT NOT NULL,
  activa    BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_personas_tenant_nombre UNIQUE (tenant_id, nombre)
);

-- Catalogo de productos
CREATE TABLE productos (
  id            SERIAL PRIMARY KEY,
  tenant_id     INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  sku           TEXT,
  nombre        TEXT NOT NULL,
  activo        BOOLEAN NOT NULL DEFAULT TRUE,
  uom_id        INTEGER NOT NULL REFERENCES uoms(id),
  marca_id      INTEGER REFERENCES marcas(id) ON DELETE SET NULL,
  categoria_id  INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
  CONSTRAINT uq_productos_tenant_sku UNIQUE (tenant_id, sku)
);

-- Movimientos de inventario (Kardex simplificado)
CREATE TABLE movimientos (
  id                 BIGSERIAL PRIMARY KEY,
  tenant_id          INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
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
    OR (
      from_locacion_id IS NOT NULL
      AND (to_locacion_id IS NULL OR to_locacion_id <> from_locacion_id)
    )
  );

ALTER TABLE movimientos ADD CONSTRAINT chk_mov_ajuste
  CHECK (
    (tipo <> 'ajuste')
    OR (from_locacion_id IS NOT NULL OR to_locacion_id IS NOT NULL)
  );

CREATE INDEX idx_users_tenant ON users (tenant_id);
CREATE INDEX idx_movimientos_tenant ON movimientos (tenant_id);
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
      WHEN m.tipo IN ('ingreso','traspaso','ajuste') AND m.to_locacion_id = l.id THEN m.cantidad
      WHEN m.tipo IN ('traspaso','uso','ajuste') AND m.from_locacion_id = l.id THEN -m.cantidad
      ELSE 0
    END
  ), 0)::NUMERIC(14,3) AS stock
FROM productos p
JOIN locaciones l
  ON l.tenant_id = p.tenant_id
LEFT JOIN movimientos m
  ON m.producto_id = p.id
  AND m.tenant_id = p.tenant_id
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
