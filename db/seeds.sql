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
  ('Suministros'),
  ('Alimentacion'),
  ('Verduras'),
  ('Condimentos'),
  ('Postres'),
  ('Helados'),
  ('Congelados'),
  ('Bebidas'),
  ('Aguas'),
  ('Limpieza')
ON CONFLICT (nombre) DO NOTHING;

-- Marcas
INSERT INTO marcas (nombre)
VALUES
  ('Granero Andino'),
  ('Vaquita Feliz'),
  ('Sin Marca'),
  ('Unilever Food Solutions'),
  ('Barilla Foodservice'),
  ('La Huerta'),
  ('McCormick'),
  ('La Costena'),
  ('Nestle Professional'),
  ('Bimbo Food Service'),
  ('Haagen-Dazs'),
  ('Helados Holanda'),
  ('McCain Foodservice'),
  ('Sigma Food Service'),
  ('Coca-Cola FEMSA'),
  ('Powerade'),
  ('Bonafont'),
  ('Perrier'),
  ('Clorox Professional'),
  ('Kimberly-Clark Professional')
ON CONFLICT (nombre) DO NOTHING;

-- Proveedores
INSERT INTO proveedores (nombre)
VALUES
  ('Nestle Professional'),
  ('Coca-Cola FEMSA'),
  ('Unilever Food Solutions'),
  ('La Costena Food Service'),
  ('La Huerta Distribuidores'),
  ('Bonafont Servicios'),
  ('Sigma Alimentos'),
  ('McCain Foodservice'),
  ('McCormick Food Service'),
  ('Clorox Professional'),
  ('Kimberly-Clark Professional'),
  ('Grupo Bimbo Food Service'),
  ('Barilla Foodservice')
ON CONFLICT (nombre) DO NOTHING;

-- Locaciones
INSERT INTO locaciones (nombre)
VALUES
  ('Bodega Central'),
  ('Cocina Principal'),
  ('Almacen Secundario'),
  ('Bodega Principal'),
  ('Cocina 1'),
  ('Cocina 2'),
  ('Parrilla'),
  ('Pasteleria'),
  ('Cocteleria')
ON CONFLICT (nombre) DO NOTHING;

-- Personas
INSERT INTO personas (nombre)
VALUES
  ('Ana Inventarios'),
  ('Luis Cocina'),
  ('Maria Compras'),
  ('Andres Compras'),
  ('Carla Pasteleria'),
  ('Diego Barra'),
  ('Sofia Parrilla'),
  ('Valeria Cocina Fria'),
  ('Roberto Limpieza')
ON CONFLICT (nombre) DO NOTHING;

-- Productos
WITH producto_data AS (
  SELECT *
  FROM (VALUES
    ('ARROZ-001', 'Arroz Granel 25kg', 'kg', 'Granero Andino', 'Granos'),
    ('LECHE-900', 'Leche Entera 900ml', 'L', 'Vaquita Feliz', 'Lacteos'),
    ('GUANTES-001', 'Guantes Desechables', 'pz', 'Sin Marca', 'Suministros'),
    ('ALIM-QSO1', 'Queso Manchego Rebanado 1kg', 'kg', 'Unilever Food Solutions', 'Alimentacion'),
    ('ALIM-PAST', 'Pasta Fusilli Gourmet 5kg', 'kg', 'Barilla Foodservice', 'Alimentacion'),
    ('VERD-MIX', 'Mix Verduras Congeladas 5kg', 'kg', 'La Huerta', 'Verduras'),
    ('VERD-BROC', 'Brocoli Floretes 2kg', 'kg', 'La Huerta', 'Verduras'),
    ('COND-PIM', 'Pimienta Negra Gourmet 500g', 'pz', 'McCormick', 'Condimentos'),
    ('COND-ADOB', 'Chile Chipotle Adobado 3kg', 'kg', 'La Costena', 'Condimentos'),
    ('POST-TRES', 'Base Tres Leches 2L', 'L', 'Nestle Professional', 'Postres'),
    ('POST-BROW', 'Mix Brownie Premium 4kg', 'kg', 'Bimbo Food Service', 'Postres'),
    ('HEL-VAN', 'Helado Vainilla 4L', 'L', 'Haagen-Dazs', 'Helados'),
    ('HEL-PALE', 'Paletas Frutas Tropicales 24pz', 'pz', 'Helados Holanda', 'Helados'),
    ('CONG-PAPA', 'Papas Corte Delgada 2.5kg', 'kg', 'McCain Foodservice', 'Congelados'),
    ('CONG-ALIT', 'Alitas de Pollo Marinadas 5kg', 'kg', 'Sigma Food Service', 'Congelados'),
    ('BEB-COLA', 'Refresco Cola 2L', 'L', 'Coca-Cola FEMSA', 'Bebidas'),
    ('BEB-HIDR', 'Bebida Isotonica 600ml', 'L', 'Powerade', 'Bebidas'),
    ('AGUA-BON', 'Agua Purificada 1L', 'L', 'Bonafont', 'Aguas'),
    ('AGUA-MIN', 'Agua Mineral 355ml', 'L', 'Perrier', 'Aguas'),
    ('LIMP-DES', 'Desinfectante Multiusos 5L', 'L', 'Clorox Professional', 'Limpieza'),
    ('LIMP-JAB', 'Jabon para Manos Espuma 1L', 'L', 'Kimberly-Clark Professional', 'Limpieza')
  ) AS d (sku, nombre, uom_abrev, marca, categoria)
)
INSERT INTO productos (sku, nombre, activo, uom_id, marca_id, categoria_id)
SELECT
  d.sku,
  d.nombre,
  TRUE,
  u.id,
  m.id,
  c.id
FROM producto_data d
JOIN uoms u ON u.abreviatura = d.uom_abrev
JOIN marcas m ON m.nombre = d.marca
JOIN categorias c ON c.nombre = d.categoria
ON CONFLICT (sku) DO NOTHING;

-- Movimientos - simulacion de un mes
WITH movimiento_data AS (
  SELECT *
  FROM (VALUES
    (TIMESTAMPTZ '2024-09-02 09:00:00+00', 'ingreso', 'ALIM-QSO1', NULL, 'Bodega Principal', 'Maria Compras', 'Nestle Professional', 40, 'Seed Sep W1 ingreso queso'),
    (TIMESTAMPTZ '2024-09-02 09:15:00+00', 'ingreso', 'ALIM-PAST', NULL, 'Bodega Principal', 'Andres Compras', 'Barilla Foodservice', 80, 'Seed Sep W1 ingreso pasta'),
    (TIMESTAMPTZ '2024-09-02 09:45:00+00', 'ingreso', 'VERD-MIX', NULL, 'Bodega Principal', 'Andres Compras', 'La Huerta Distribuidores', 60, 'Seed Sep W1 ingreso mix verduras'),
    (TIMESTAMPTZ '2024-09-02 10:15:00+00', 'ingreso', 'BEB-COLA', NULL, 'Bodega Principal', 'Maria Compras', 'Coca-Cola FEMSA', 150, 'Seed Sep W1 ingreso refrescos'),
    (TIMESTAMPTZ '2024-09-02 10:45:00+00', 'ingreso', 'AGUA-BON', NULL, 'Bodega Principal', 'Maria Compras', 'Bonafont Servicios', 220, 'Seed Sep W1 ingreso agua purificada'),
    (TIMESTAMPTZ '2024-09-02 11:15:00+00', 'ingreso', 'LIMP-DES', NULL, 'Bodega Principal', 'Ana Inventarios', 'Clorox Professional', 30, 'Seed Sep W1 ingreso desinfectante'),
    (TIMESTAMPTZ '2024-09-03 08:00:00+00', 'traspaso', 'ALIM-QSO1', 'Bodega Principal', 'Cocina 1', 'Ana Inventarios', NULL, 8, 'Seed Sep W1 traspaso queso a cocina 1'),
    (TIMESTAMPTZ '2024-09-03 08:20:00+00', 'traspaso', 'VERD-MIX', 'Bodega Principal', 'Cocina 1', 'Ana Inventarios', NULL, 15, 'Seed Sep W1 traspaso verduras a cocina 1'),
    (TIMESTAMPTZ '2024-09-03 08:40:00+00', 'traspaso', 'BEB-COLA', 'Bodega Principal', 'Cocteleria', 'Diego Barra', NULL, 40, 'Seed Sep W1 traspaso refrescos a barra'),
    (TIMESTAMPTZ '2024-09-03 09:00:00+00', 'traspaso', 'AGUA-BON', 'Bodega Principal', 'Cocina 2', 'Valeria Cocina Fria', NULL, 60, 'Seed Sep W1 traspaso agua a cocina 2'),
    (TIMESTAMPTZ '2024-09-03 09:20:00+00', 'traspaso', 'LIMP-DES', 'Bodega Principal', 'Cocina 1', 'Roberto Limpieza', NULL, 6, 'Seed Sep W1 traspaso desinfectante cocina 1'),
    (TIMESTAMPTZ '2024-09-03 18:00:00+00', 'uso', 'VERD-MIX', 'Cocina 1', NULL, 'Luis Cocina', NULL, 6, 'Seed Sep W1 uso verduras servicio comida'),
    (TIMESTAMPTZ '2024-09-04 09:00:00+00', 'traspaso', 'ALIM-PAST', 'Bodega Principal', 'Cocina 2', 'Ana Inventarios', NULL, 20, 'Seed Sep W1 traspaso pasta cocina 2'),
    (TIMESTAMPTZ '2024-09-04 11:30:00+00', 'uso', 'ALIM-QSO1', 'Cocina 1', NULL, 'Luis Cocina', NULL, 3, 'Seed Sep W1 uso queso cena especial'),
    (TIMESTAMPTZ '2024-09-04 17:30:00+00', 'uso', 'ALIM-PAST', 'Cocina 2', NULL, 'Valeria Cocina Fria', NULL, 12, 'Seed Sep W1 uso pasta comida ejecutiva'),
    (TIMESTAMPTZ '2024-09-04 22:00:00+00', 'uso', 'BEB-COLA', 'Cocteleria', NULL, 'Diego Barra', NULL, 18, 'Seed Sep W1 uso refrescos noche'),
    (TIMESTAMPTZ '2024-09-05 07:30:00+00', 'uso', 'LIMP-DES', 'Cocina 1', NULL, 'Roberto Limpieza', NULL, 2, 'Seed Sep W1 uso desinfectante pasillos'),
    (TIMESTAMPTZ '2024-09-05 16:00:00+00', 'uso', 'AGUA-BON', 'Cocina 2', NULL, 'Valeria Cocina Fria', NULL, 25, 'Seed Sep W1 uso agua cocina 2'),
    (TIMESTAMPTZ '2024-09-09 09:00:00+00', 'ingreso', 'POST-TRES', NULL, 'Bodega Principal', 'Maria Compras', 'Nestle Professional', 35, 'Seed Sep W2 ingreso base tres leches'),
    (TIMESTAMPTZ '2024-09-09 09:15:00+00', 'ingreso', 'POST-BROW', NULL, 'Bodega Principal', 'Andres Compras', 'Grupo Bimbo Food Service', 25, 'Seed Sep W2 ingreso mix brownie'),
    (TIMESTAMPTZ '2024-09-09 09:30:00+00', 'ingreso', 'HEL-VAN', NULL, 'Bodega Principal', 'Maria Compras', 'Nestle Professional', 18, 'Seed Sep W2 ingreso helado vainilla'),
    (TIMESTAMPTZ '2024-09-09 09:45:00+00', 'ingreso', 'HEL-PALE', NULL, 'Bodega Principal', 'Andres Compras', 'Unilever Food Solutions', 24, 'Seed Sep W2 ingreso paletas'),
    (TIMESTAMPTZ '2024-09-09 10:00:00+00', 'ingreso', 'LIMP-JAB', NULL, 'Bodega Principal', 'Roberto Limpieza', 'Kimberly-Clark Professional', 28, 'Seed Sep W2 ingreso jabon manos'),
    (TIMESTAMPTZ '2024-09-10 08:00:00+00', 'traspaso', 'POST-TRES', 'Bodega Principal', 'Pasteleria', 'Carla Pasteleria', NULL, 10, 'Seed Sep W2 traspaso base tres leches'),
    (TIMESTAMPTZ '2024-09-10 08:20:00+00', 'traspaso', 'POST-BROW', 'Bodega Principal', 'Pasteleria', 'Carla Pasteleria', NULL, 8, 'Seed Sep W2 traspaso mix brownie'),
    (TIMESTAMPTZ '2024-09-10 08:40:00+00', 'traspaso', 'HEL-VAN', 'Bodega Principal', 'Pasteleria', 'Carla Pasteleria', NULL, 6, 'Seed Sep W2 traspaso helado vainilla'),
    (TIMESTAMPTZ '2024-09-10 09:00:00+00', 'traspaso', 'HEL-PALE', 'Bodega Principal', 'Cocteleria', 'Diego Barra', NULL, 12, 'Seed Sep W2 traspaso paletas barra'),
    (TIMESTAMPTZ '2024-09-10 09:20:00+00', 'traspaso', 'LIMP-JAB', 'Bodega Principal', 'Cocina 2', 'Roberto Limpieza', NULL, 10, 'Seed Sep W2 traspaso jabon cocina 2'),
    (TIMESTAMPTZ '2024-09-11 16:00:00+00', 'uso', 'POST-TRES', 'Pasteleria', NULL, 'Carla Pasteleria', NULL, 4, 'Seed Sep W2 uso base pastel tres leches'),
    (TIMESTAMPTZ '2024-09-11 16:30:00+00', 'uso', 'POST-BROW', 'Pasteleria', NULL, 'Carla Pasteleria', NULL, 3, 'Seed Sep W2 uso mix brownie'),
    (TIMESTAMPTZ '2024-09-11 21:00:00+00', 'uso', 'HEL-VAN', 'Pasteleria', NULL, 'Carla Pasteleria', NULL, 2, 'Seed Sep W2 uso helado vainilla'),
    (TIMESTAMPTZ '2024-09-12 21:30:00+00', 'uso', 'HEL-PALE', 'Cocteleria', NULL, 'Diego Barra', NULL, 6, 'Seed Sep W2 uso paletas cocteleria'),
    (TIMESTAMPTZ '2024-09-13 07:30:00+00', 'uso', 'LIMP-JAB', 'Cocina 2', NULL, 'Roberto Limpieza', NULL, 2, 'Seed Sep W2 uso jabon manos'),
    (TIMESTAMPTZ '2024-09-16 08:30:00+00', 'ingreso', 'CONG-PAPA', NULL, 'Bodega Principal', 'Andres Compras', 'McCain Foodservice', 90, 'Seed Sep W3 ingreso papas congeladas'),
    (TIMESTAMPTZ '2024-09-16 09:00:00+00', 'ingreso', 'CONG-ALIT', NULL, 'Bodega Principal', 'Maria Compras', 'Sigma Alimentos', 70, 'Seed Sep W3 ingreso alitas'),
    (TIMESTAMPTZ '2024-09-16 09:30:00+00', 'ingreso', 'BEB-HIDR', NULL, 'Bodega Principal', 'Maria Compras', 'Coca-Cola FEMSA', 120, 'Seed Sep W3 ingreso bebida isotonica'),
    (TIMESTAMPTZ '2024-09-16 09:50:00+00', 'ingreso', 'AGUA-MIN', NULL, 'Bodega Principal', 'Maria Compras', 'Nestle Professional', 80, 'Seed Sep W3 ingreso agua mineral'),
    (TIMESTAMPTZ '2024-09-16 10:10:00+00', 'ingreso', 'COND-PIM', NULL, 'Bodega Principal', 'Andres Compras', 'McCormick Food Service', 25, 'Seed Sep W3 ingreso pimienta'),
    (TIMESTAMPTZ '2024-09-16 10:30:00+00', 'ingreso', 'COND-ADOB', NULL, 'Bodega Principal', 'Maria Compras', 'La Costena Food Service', 40, 'Seed Sep W3 ingreso chipotle'),
    (TIMESTAMPTZ '2024-09-17 08:00:00+00', 'traspaso', 'CONG-PAPA', 'Bodega Principal', 'Parrilla', 'Sofia Parrilla', NULL, 25, 'Seed Sep W3 traspaso papas parrilla'),
    (TIMESTAMPTZ '2024-09-17 08:20:00+00', 'traspaso', 'CONG-ALIT', 'Bodega Principal', 'Parrilla', 'Sofia Parrilla', NULL, 20, 'Seed Sep W3 traspaso alitas parrilla'),
    (TIMESTAMPTZ '2024-09-17 08:40:00+00', 'traspaso', 'BEB-HIDR', 'Bodega Principal', 'Cocina 2', 'Valeria Cocina Fria', NULL, 50, 'Seed Sep W3 traspaso bebida isotonica'),
    (TIMESTAMPTZ '2024-09-17 09:00:00+00', 'traspaso', 'AGUA-MIN', 'Bodega Principal', 'Cocteleria', 'Diego Barra', NULL, 30, 'Seed Sep W3 traspaso agua mineral barra'),
    (TIMESTAMPTZ '2024-09-17 09:20:00+00', 'traspaso', 'COND-PIM', 'Bodega Principal', 'Cocina 1', 'Ana Inventarios', NULL, 6, 'Seed Sep W3 traspaso pimienta cocina 1'),
    (TIMESTAMPTZ '2024-09-17 09:40:00+00', 'traspaso', 'COND-ADOB', 'Bodega Principal', 'Cocina 1', 'Ana Inventarios', NULL, 10, 'Seed Sep W3 traspaso chipotle cocina 1'),
    (TIMESTAMPTZ '2024-09-18 13:00:00+00', 'uso', 'CONG-PAPA', 'Parrilla', NULL, 'Sofia Parrilla', NULL, 12, 'Seed Sep W3 uso papas almuerzo'),
    (TIMESTAMPTZ '2024-09-18 20:00:00+00', 'uso', 'CONG-ALIT', 'Parrilla', NULL, 'Sofia Parrilla', NULL, 10, 'Seed Sep W3 uso alitas noche'),
    (TIMESTAMPTZ '2024-09-19 12:30:00+00', 'uso', 'BEB-HIDR', 'Cocina 2', NULL, 'Valeria Cocina Fria', NULL, 18, 'Seed Sep W3 uso bebida isotonica staff'),
    (TIMESTAMPTZ '2024-09-19 21:00:00+00', 'uso', 'AGUA-MIN', 'Cocteleria', NULL, 'Diego Barra', NULL, 10, 'Seed Sep W3 uso agua mineral barra'),
    (TIMESTAMPTZ '2024-09-20 14:00:00+00', 'uso', 'COND-PIM', 'Cocina 1', NULL, 'Luis Cocina', NULL, 2, 'Seed Sep W3 uso pimienta salsa'),
    (TIMESTAMPTZ '2024-09-20 14:15:00+00', 'uso', 'COND-ADOB', 'Cocina 1', NULL, 'Luis Cocina', NULL, 3, 'Seed Sep W3 uso chipotle adobo'),
    (TIMESTAMPTZ '2024-09-24 09:00:00+00', 'ingreso', 'HEL-VAN', NULL, 'Bodega Principal', 'Maria Compras', 'Nestle Professional', 12, 'Seed Sep W4 refuerzo helado vainilla'),
    (TIMESTAMPTZ '2024-09-24 09:20:00+00', 'ingreso', 'HEL-PALE', NULL, 'Bodega Principal', 'Andres Compras', 'Unilever Food Solutions', 18, 'Seed Sep W4 refuerzo paletas'),
    (TIMESTAMPTZ '2024-09-25 08:00:00+00', 'traspaso', 'HEL-VAN', 'Bodega Principal', 'Pasteleria', 'Carla Pasteleria', NULL, 4, 'Seed Sep W4 traspaso helado refuerzo'),
    (TIMESTAMPTZ '2024-09-25 08:20:00+00', 'traspaso', 'HEL-PALE', 'Bodega Principal', 'Cocteleria', 'Diego Barra', NULL, 8, 'Seed Sep W4 traspaso paletas evento'),
    (TIMESTAMPTZ '2024-09-25 17:00:00+00', 'uso', 'HEL-VAN', 'Pasteleria', NULL, 'Carla Pasteleria', NULL, 2, 'Seed Sep W4 uso helado tarde'),
    (TIMESTAMPTZ '2024-09-25 21:30:00+00', 'uso', 'HEL-PALE', 'Cocteleria', NULL, 'Diego Barra', NULL, 5, 'Seed Sep W4 uso paletas evento'),
    (TIMESTAMPTZ '2024-09-27 11:00:00+00', 'uso', 'POST-BROW', 'Pasteleria', NULL, 'Carla Pasteleria', NULL, 2, 'Seed Sep W4 uso mix brownie brunch')
  ) AS md (fecha, tipo, sku, from_locacion, to_locacion, persona, proveedor, cantidad, nota)
)
INSERT INTO movimientos (
  fecha,
  tipo,
  producto_id,
  from_locacion_id,
  to_locacion_id,
  persona_id,
  proveedor_id,
  cantidad,
  nota
)
SELECT
  md.fecha,
  md.tipo::tipo_movimiento,
  p.id,
  fl.id,
  tl.id,
  per.id,
  prov.id,
  md.cantidad,
  md.nota
FROM movimiento_data md
JOIN productos p ON p.sku = md.sku
LEFT JOIN locaciones fl ON fl.nombre = md.from_locacion
LEFT JOIN locaciones tl ON tl.nombre = md.to_locacion
JOIN personas per ON per.nombre = md.persona
LEFT JOIN proveedores prov ON prov.nombre = md.proveedor
WHERE NOT EXISTS (
  SELECT 1
  FROM movimientos existing
  WHERE existing.nota = md.nota
);

COMMIT;
