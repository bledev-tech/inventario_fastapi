BEGIN;

-- Unidades de medida
INSERT INTO uoms (nombre, abreviatura, descripcion)
VALUES
  ('Kilogramo', 'kg', 'Unidad base para ingredientes secos'),
  ('Litro', 'L', 'Liquidos y aceites'),
  ('Pieza', 'pz', 'Elementos individuales (vajilla, equipo)')
ON CONFLICT (nombre) DO NOTHING;

-- Categorias
INSERT INTO categorias (nombre)
VALUES
  ('Granos'),
  ('Lacteos'),
  ('Suministros')
ON CONFLICT (nombre) DO NOTHING;

-- Marcas
INSERT INTO marcas (nombre)
VALUES
  ('Granero Andino'),
  ('Vaquita Feliz'),
  ('Sin Marca')
ON CONFLICT (nombre) DO NOTHING;

-- Proveedores
INSERT INTO proveedores (nombre)
VALUES
  ('Proveedor Central'),
  ('Productos del Norte'),
  ('Limpieza Express')
ON CONFLICT (nombre) DO NOTHING;

-- Locaciones
INSERT INTO locaciones (nombre)
VALUES
  ('Bodega Central'),
  ('Cocina Principal'),
  ('Almacen Secundario')
ON CONFLICT (nombre) DO NOTHING;

-- Personas
INSERT INTO personas (nombre)
VALUES
  ('Ana Inventarios'),
  ('Luis Cocina'),
  ('Maria Compras')
ON CONFLICT (nombre) DO NOTHING;

-- Productos
INSERT INTO productos (sku, nombre, activo, uom_id, marca_id, categoria_id)
SELECT
  'ARROZ-001',
  'Arroz Granel 25kg',
  TRUE,
  u.id,
  m.id,
  c.id
FROM uoms u
JOIN marcas m ON m.nombre = 'Granero Andino'
JOIN categorias c ON c.nombre = 'Granos'
WHERE u.abreviatura = 'kg'
  AND NOT EXISTS (SELECT 1 FROM productos WHERE sku = 'ARROZ-001');

INSERT INTO productos (sku, nombre, activo, uom_id, marca_id, categoria_id)
SELECT
  'LECHE-900',
  'Leche Entera 900ml',
  TRUE,
  u.id,
  m.id,
  c.id
FROM uoms u
JOIN marcas m ON m.nombre = 'Vaquita Feliz'
JOIN categorias c ON c.nombre = 'Lacteos'
WHERE u.abreviatura = 'L'
  AND NOT EXISTS (SELECT 1 FROM productos WHERE sku = 'LECHE-900');

INSERT INTO productos (sku, nombre, activo, uom_id, marca_id, categoria_id)
SELECT
  'GUANTES-001',
  'Guantes Desechables',
  TRUE,
  u.id,
  m.id,
  c.id
FROM uoms u
JOIN marcas m ON m.nombre = 'Sin Marca'
JOIN categorias c ON c.nombre = 'Suministros'
WHERE u.abreviatura = 'pz'
  AND NOT EXISTS (SELECT 1 FROM productos WHERE sku = 'GUANTES-001');

-- Movimientos de ejemplo
INSERT INTO movimientos (tipo, producto_id, to_locacion_id, persona_id, proveedor_id, cantidad, nota)
SELECT
  'ingreso',
  p.id,
  l.id,
  per.id,
  prov.id,
  50,
  'Seed: ingreso inicial arroz'
FROM productos p
JOIN locaciones l ON l.nombre = 'Bodega Central'
JOIN personas per ON per.nombre = 'Maria Compras'
JOIN proveedores prov ON prov.nombre = 'Proveedor Central'
WHERE p.sku = 'ARROZ-001'
  AND NOT EXISTS (
    SELECT 1 FROM movimientos
    WHERE nota = 'Seed: ingreso inicial arroz'
  );

INSERT INTO movimientos (tipo, producto_id, to_locacion_id, persona_id, proveedor_id, cantidad, nota)
SELECT
  'ingreso',
  p.id,
  l.id,
  per.id,
  prov.id,
  120,
  'Seed: ingreso inicial leche'
FROM productos p
JOIN locaciones l ON l.nombre = 'Bodega Central'
JOIN personas per ON per.nombre = 'Maria Compras'
JOIN proveedores prov ON prov.nombre = 'Productos del Norte'
WHERE p.sku = 'LECHE-900'
  AND NOT EXISTS (
    SELECT 1 FROM movimientos
    WHERE nota = 'Seed: ingreso inicial leche'
  );

INSERT INTO movimientos (tipo, producto_id, to_locacion_id, persona_id, proveedor_id, cantidad, nota)
SELECT
  'ingreso',
  p.id,
  l.id,
  per.id,
  prov.id,
  300,
  'Seed: ingreso inicial guantes'
FROM productos p
JOIN locaciones l ON l.nombre = 'Almacen Secundario'
JOIN personas per ON per.nombre = 'Ana Inventarios'
JOIN proveedores prov ON prov.nombre = 'Limpieza Express'
WHERE p.sku = 'GUANTES-001'
  AND NOT EXISTS (
    SELECT 1 FROM movimientos
    WHERE nota = 'Seed: ingreso inicial guantes'
  );

-- Movimiento de uso para consumir parte del stock
INSERT INTO movimientos (tipo, producto_id, from_locacion_id, persona_id, cantidad, nota)
SELECT
  'uso',
  p.id,
  l.id,
  per.id,
  5,
  'Seed: uso cocina arroz'
FROM productos p
JOIN locaciones l ON l.nombre = 'Bodega Central'
JOIN personas per ON per.nombre = 'Luis Cocina'
WHERE p.sku = 'ARROZ-001'
  AND NOT EXISTS (
    SELECT 1 FROM movimientos
    WHERE nota = 'Seed: uso cocina arroz'
  );

COMMIT;
