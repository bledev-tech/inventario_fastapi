BEGIN;

-- Unidades de medida base
INSERT INTO uoms (nombre, abreviatura, descripcion)
VALUES
  ('Kilogramo', 'kg', 'Peso en kilogramos para alimentos'),
  ('Litro', 'L', 'Volumen en litros para liquidos'),
  ('Unidad', 'pz', 'Piezas individuales o empaques contados')
ON CONFLICT (nombre) DO NOTHING;

-- Categorias consolidadas para una vista mas simple
INSERT INTO categorias (nombre)
VALUES
  ('Despensa y aceites'),
  ('Condimentos y especias'),
  ('Proteinas y carnes'),
  ('Frutas y verduras frescas'),
  ('Congelados y precocidos'),
  ('Postres, lacteos y panaderia'),
  ('Bebidas sin alcohol'),
  ('Cervezas y espumantes'),
  ('Vinos'),
  ('Destilados y licores'),
  ('Operaciones y limpieza')
ON CONFLICT (nombre) DO NOTHING;

-- Marcas depuradas (solo las que se usan abajo)
INSERT INTO marcas (nombre)
VALUES
  ('Sin Marca'),
  ('Miraflores'),
  ('San Remo'),
  ('Nestle'),
  ('Colun'),
  ('Andina'),
  ('Coca-Cola'),
  ('Valdivieso'),
  ('Amaranta'),
  ('Austral'),
  ('Kunstmann'),
  ('Dalbosco'),
  ('Carmen'),
  ('120'),
  ('Casillero Del Diablo'),
  ('8 Tierras'),
  ('Mistral'),
  ('Alto Del Carmen'),
  ('Mal Paso'),
  ('Stolichnaya'),
  ('Eristoff'),
  ('Beefeater'),
  ('Rossard'),
  ('Aperol'),
  ('Bacardi'),
  ('Havana Club'),
  ('Sombrero Negro'),
  ('Johnnie Walker'),
  ('Jack Daniels')
ON CONFLICT (nombre) DO NOTHING;

-- Proveedores referenciales
INSERT INTO proveedores (nombre)
VALUES
  ('Agrosuper'),
  ('Bidfood'),
  ('Coca-Cola'),
  ('Distribuidora Bebidas'),
  ('Distribuidora Vinos y Licores'),
  ('Proveedores Varios Calameno')
ON CONFLICT (nombre) DO NOTHING;

-- Locaciones operativas
INSERT INTO locaciones (nombre)
VALUES
  ('Bodega Calameno'),
  ('Camara Fria Calameno'),
  ('Bar Calameno'),
  ('Operaciones Calameno')
ON CONFLICT (nombre) DO NOTHING;

-- Personas responsables
INSERT INTO personas (nombre)
VALUES
  ('Angel Calameno'),
  ('Equipo Bar Calameno'),
  ('Equipo Cocina Calameno'),
  ('Equipo Operaciones Calameno')
ON CONFLICT (nombre) DO NOTHING;

-- Productos depurados y ordenados por categoria
WITH producto_data AS (
  SELECT * FROM (VALUES
    -- Despensa y aceites
    ('CAL-0001', 'Aceite Vegetal 900 ml', 'L', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0002', 'Aceite de Freir 5 L', 'L', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0003', 'Aceite de Oliva 5 L', 'L', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0005', 'Arroz Grano Largo 1 kg', 'kg', 'Miraflores', 'Despensa y aceites'),
    ('CAL-0006', 'Azucar Blanca 1 kg', 'kg', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0007', 'Azucar Flor 1 kg', 'kg', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0019', 'Harina de Trigo 25 kg', 'kg', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0023', 'Ketchup a Granel 1 kg', 'kg', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0028', 'Mayonesa Food Service', 'pz', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0031', 'Mostaza', 'pz', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0032', 'Quinoa Blanca', 'pz', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0034', 'Sal Fina', 'pz', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0035', 'Sal Parrillera', 'pz', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0036', 'Salsa de Tomate 1 kg', 'pz', 'San Remo', 'Despensa y aceites'),
    ('CAL-0039', 'Spaghetti 400 g', 'kg', 'Sin Marca', 'Despensa y aceites'),
    ('CAL-0040', 'Spaghetti 5 kg', 'kg', 'Sin Marca', 'Despensa y aceites'),

    -- Condimentos y especias
    ('CAL-0157', 'Aji Color', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0159', 'Canela en Polvo', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0162', 'Clavo de Olor', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0163', 'Comino Molido', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0164', 'Laurel Hoja', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0166', 'Merken', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0167', 'Oregano', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0168', 'Pimienta en Polvo', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0169', 'Pimienta Entera', 'pz', 'Sin Marca', 'Condimentos y especias'),
    ('CAL-0171', 'Romero', 'pz', 'Sin Marca', 'Condimentos y especias'),

    -- Proteinas y carnes
    ('CAL-0108', 'Bistec 200 g', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0109', 'Carne Molida Corriente 500 g', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0110', 'Carne Molida Especial', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0113', 'Camaron 500 g', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0116', 'Chorizos 1 kg', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0131', 'Hamburguesa', 'pz', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0134', 'Lomo Vetado 200 g', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0135', 'Lomo Vetado 300 g', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0137', 'Mariscos Surtido', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0142', 'Pulpa de Cerdo', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0144', 'Suprema de Pechuga Deshuesada', 'kg', 'Sin Marca', 'Proteinas y carnes'),
    ('CAL-0147', 'Tuto Pollo', 'kg', 'Sin Marca', 'Proteinas y carnes'),

    -- Frutas y verduras frescas
    ('CAL-0358', 'Ajos', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0365', 'Cebolla', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0366', 'Cebolla Morada', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0377', 'Lechugas Hidroponicas', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0378', 'Limon', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0385', 'Palta', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0386', 'Papas', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0389', 'Pimenton Rojo', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0390', 'Pimenton Verde', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0396', 'Tomates', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0397', 'Tomates Cherry', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),
    ('CAL-0398', 'Zanahorias', 'kg', 'Sin Marca', 'Frutas y verduras frescas'),

    -- Congelados y precocidos
    ('CAL-0174', 'Arvejas 500 g', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0175', 'Choclo Grano 1 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0176', 'Choclo Trozo 2 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0177', 'Frutillas 1 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0178', 'Masas de Cocktail', 'pz', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0179', 'Masas Empanada', 'pz', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0180', 'Nuggets 2.5 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0181', 'Papas Duquesa', 'pz', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0182', 'Pastelera 1 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0184', 'Primavera 2 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0185', 'Pulpa Berries 1 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0186', 'Pulpa Mango 1 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),
    ('CAL-0187', 'Pulpa Maracuya 1 kg', 'kg', 'Sin Marca', 'Congelados y precocidos'),

    -- Postres, lacteos y panaderia
    ('CAL-0316', 'Crema de Leche 1 L', 'L', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0323', 'Gelatina Sin Sabor 1 kg', 'kg', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0324', 'Huevos', 'pz', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0326', 'Leche Condensada', 'pz', 'Nestle', 'Postres, lacteos y panaderia'),
    ('CAL-0327', 'Leche en Polvo 1 kg', 'kg', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0328', 'Leche Evaporada', 'pz', 'Nestle', 'Postres, lacteos y panaderia'),
    ('CAL-0329', 'Leche Entera 1 L', 'L', 'Colun', 'Postres, lacteos y panaderia'),
    ('CAL-0330', 'Levadura', 'pz', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0331', 'Maicena 500 g', 'pz', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0332', 'Manjar 1 kg', 'kg', 'Nestle', 'Postres, lacteos y panaderia'),
    ('CAL-0335', 'Mantequilla 250 g', 'pz', 'Colun', 'Postres, lacteos y panaderia'),
    ('CAL-0336', 'Mantequilla Sachet Individual', 'pz', 'Colun', 'Postres, lacteos y panaderia'),
    ('CAL-0348', 'Polvo de Hornear 500 g', 'pz', 'Sin Marca', 'Postres, lacteos y panaderia'),
    ('CAL-0349', 'Queso Amarillo', 'pz', 'Sin Marca', 'Postres, lacteos y panaderia'),

    -- Bebidas sin alcohol
    ('CAL-0044', 'Agua Bidon 20 L', 'L', 'Sin Marca', 'Bebidas sin alcohol'),
    ('CAL-0045', 'Agua Con Gas 1.5 L', 'L', 'Sin Marca', 'Bebidas sin alcohol'),
    ('CAL-0047', 'Agua Sin Gas 1.5 L', 'L', 'Sin Marca', 'Bebidas sin alcohol'),
    ('CAL-0096', 'Coca-Cola 1.5 L', 'L', 'Coca-Cola', 'Bebidas sin alcohol'),
    ('CAL-0098', 'Coca-Cola Zero 350 ml', 'L', 'Coca-Cola', 'Bebidas sin alcohol'),
    ('CAL-0100', 'Coca-Cola 350 ml', 'L', 'Coca-Cola', 'Bebidas sin alcohol'),
    ('CAL-0102', 'Fanta 350 ml', 'L', 'Coca-Cola', 'Bebidas sin alcohol'),
    ('CAL-0104', 'Red Bull 250 ml', 'L', 'Sin Marca', 'Bebidas sin alcohol'),
    ('CAL-0105', 'Sprite 1.5 L', 'L', 'Coca-Cola', 'Bebidas sin alcohol'),
    ('CAL-0107', 'Sprite 350 ml', 'L', 'Coca-Cola', 'Bebidas sin alcohol'),
    ('CAL-0238', 'Jugo Botellin Durazno 400 ml', 'L', 'Andina', 'Bebidas sin alcohol'),
    ('CAL-0239', 'Jugo Botellin Naranja 400 ml', 'L', 'Andina', 'Bebidas sin alcohol'),
    ('CAL-0243', 'Nectar 1.5 L', 'L', 'Andina', 'Bebidas sin alcohol'),

    -- Cervezas y espumantes
    ('CAL-0152', 'Cerveza Lager 330 ml', 'pz', 'Austral', 'Cervezas y espumantes'),
    ('CAL-0154', 'Cerveza Miel 330 ml', 'L', 'Kunstmann', 'Cervezas y espumantes'),
    ('CAL-0156', 'Cerveza Torobayo 330 ml', 'L', 'Kunstmann', 'Cervezas y espumantes'),
    ('CAL-0189', 'Espumante Brut 375 ml', 'L', 'Amaranta', 'Cervezas y espumantes'),
    ('CAL-0190', 'Espumante Demi Sec 750 ml', 'L', 'Amaranta', 'Cervezas y espumantes'),
    ('CAL-0192', 'Espumante Brut 750 ml', 'L', 'Valdivieso', 'Cervezas y espumantes'),
    ('CAL-0194', 'Espumante Demi Sec 750 ml', 'L', 'Valdivieso', 'Cervezas y espumantes'),
    ('CAL-0196', 'Espumante Moscato 750 ml', 'L', 'Valdivieso', 'Cervezas y espumantes'),

    -- Vinos
    ('CAL-0406', 'Cabernet Sauvignon 750 ml', 'L', 'Dalbosco', 'Vinos'),
    ('CAL-0407', 'Carmenere MGX 750 ml', 'L', 'Carmen', 'Vinos'),
    ('CAL-0411', 'Clasico Cabernet Sauvignon 375 ml', 'L', '120', 'Vinos'),
    ('CAL-0413', 'Clasico Merlot 750 ml', 'L', 'Carmen', 'Vinos'),
    ('CAL-0417', 'Cabernet Sauvignon 750 ml', 'L', 'Casillero Del Diablo', 'Vinos'),
    ('CAL-0418', 'Gran Reserva Carmenere 750 ml', 'L', 'Dalbosco', 'Vinos'),
    ('CAL-0424', 'Reserva Especial Cabernet Sauvignon 750 ml', 'L', '8 Tierras', 'Vinos'),
    ('CAL-0427', 'Reserva Privada Syrah 750 ml', 'L', '8 Tierras', 'Vinos'),
    ('CAL-0428', 'Rose 750 ml', 'L', 'Dalbosco', 'Vinos'),

    -- Destilados y licores
    ('CAL-0245', 'Aperol 750 ml', 'L', 'Aperol', 'Destilados y licores'),
    ('CAL-0252', 'Fernet 1 L', 'L', 'Rossard', 'Destilados y licores'),
    ('CAL-0254', 'Gin London Dry', 'L', 'Beefeater', 'Destilados y licores'),
    ('CAL-0263', 'Tequila 750 ml', 'L', 'Sombrero Negro', 'Destilados y licores'),
    ('CAL-0265', 'Vodka 1 L', 'L', 'Stolichnaya', 'Destilados y licores'),
    ('CAL-0266', 'Vodka 700 ml', 'L', 'Eristoff', 'Destilados y licores'),
    ('CAL-0269', 'Pisco Apple 35 750 ml', 'L', 'Mistral', 'Destilados y licores'),
    ('CAL-0271', 'Pisco Anjeado en Roble 40 750 ml', 'L', 'Mistral', 'Destilados y licores'),
    ('CAL-0273', 'Pisco Especial 35 750 ml', 'L', 'Mal Paso', 'Destilados y licores'),
    ('CAL-0274', 'Pisco Especial 35 750 ml', 'L', 'Alto Del Carmen', 'Destilados y licores'),
    ('CAL-0280', 'Ron 1 L', 'L', 'Havana Club', 'Destilados y licores'),
    ('CAL-0281', 'Ron Blanco 1.75 L', 'L', 'Bacardi', 'Destilados y licores'),
    ('CAL-0439', 'Whisky Black Label 750 ml', 'L', 'Johnnie Walker', 'Destilados y licores'),
    ('CAL-0440', 'Whisky No 7 750 ml', 'L', 'Jack Daniels', 'Destilados y licores'),

    -- Operaciones y limpieza
    ('CAL-0052', 'Bolsa Basura 110x130', 'kg', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0056', 'Bolsa Basura 70x90', 'kg', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0062', 'Cloro Gel 5 L', 'L', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0066', 'Desengrasante 5 L', 'L', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0069', 'Escobillon', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0070', 'Esponjas', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0072', 'Guantes de Latex Negro', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0074', 'Jabon Liquido 5 L', 'L', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0078', 'Lavaloza 5 L', 'L', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0079', 'Limpia Pisos 5 L', 'L', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0080', 'Limpia Vidrios', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0086', 'Servilleta Doble Hoja', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0088', 'Toalla Nova', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0284', 'Aluminio 30x110 m', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0285', 'Alusa Film', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0293', 'Bombillas 100 uni', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0296', 'Cuchara Plastico 100 uni', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0297', 'Cuchillo Plastico 100 uni', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0306', 'Tapa de Vaso', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0307', 'Tenedor Plastico 100 uni', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0308', 'Vaso Chico 250 cc', 'pz', 'Sin Marca', 'Operaciones y limpieza'),
    ('CAL-0309', 'Vaso Mediano 500 cc', 'pz', 'Sin Marca', 'Operaciones y limpieza')
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
ON CONFLICT (sku) DO UPDATE SET
  nombre = EXCLUDED.nombre,
  activo = EXCLUDED.activo,
  uom_id = EXCLUDED.uom_id,
  marca_id = EXCLUDED.marca_id,
  categoria_id = EXCLUDED.categoria_id;

COMMIT;
