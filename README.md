# Inventario FastAPI MVP

MVP interno para gestionar inventario de cocina con FastAPI y PostgreSQL, manteniendo la logica de negocio en la base de datos (checks, tipos, vista de stock y trigger anti stock negativo).

## Requisitos

- Docker y Docker Compose
- Opcional: Python 3.11+ para ejecutar la aplicacion fuera de contenedores

## Configuracion rapida

1. Copia el archivo de ejemplo y ajusta credenciales si es necesario:
   ```bash
   cp .env.example .env
   ```
2. Construye y levanta los servicios:
   ```bash
   docker-compose up --build
   ```
3. La API queda disponible en `http://localhost:8000` y la base de datos en `localhost:5432`.

La base de datos se inicializa automaticamente con el esquema provisto (`db/schema.sql`), que define:
- Tipo `tipo_movimiento`
- Tablas `productos`, `locaciones`, `personas`, `movimientos`
- Vista `vista_stock_actual`
- Trigger `tg_evitar_stock_negativo` y funcion `fn_evitar_stock_negativo`

## Arquitectura

- `app/main.py`: crea la instancia de FastAPI y monta el router versionado.
- `app/api/v1/endpoints`: controladores HTTP divididos por dominio (productos, locaciones, personas, movimientos y stock).
- `app/crud`: operaciones basicas con SQLAlchemy ajustadas a cada modelo.
- `app/models`: modelos ORM y enums compartidos con los esquemas Pydantic.
- `app/schemas`: contratos de entrada/salida en la API. Incluyen validaciones de negocio de primer nivel.
- `db/schema.sql`: esquema fuente de la logica de negocio en PostgreSQL (checks y trigger anti stock negativo).

## Reglas de negocio clave

- Todo movimiento registra cantidades positivas (`NUMERIC(14,3)`).
- Las reglas por tipo de movimiento son:
  - `ingreso`: requiere `to_locacion_id` y prohibe `from_locacion_id`.
  - `traspaso`: requiere ambos IDs de locacion y deben ser distintos.
  - `uso`: requiere `from_locacion_id` y prohibe `to_locacion_id`.
  - `ajuste`: permite una locacion de origen o destino; dejar ambos nulos no esta permitido.
- El trigger `fn_evitar_stock_negativo` bloquea usos y traspasos que dejen stock negativo en la locacion origen.
- SKU de producto es opcional, pero si se informa debe ser unico.
- Los nombres de locacion deben ser unicos.
- Las personas deben tener nombre unico; pueden desactivarse via `activa=false` y aun asi quedar vinculadas a movimientos historicos.

Las validaciones anteriores se aplican primero en la API (errores 422/400) y luego se refuerzan en la base de datos.

## Endpoints principales

- `GET /` - health check basico.
- `GET /docs` - documentacion interactiva (Swagger UI).
- `GET /redoc` - documentacion alternativa.
- `GET /api/v1/productos` - catalogo de productos.
- `GET /api/v1/locaciones` - catalogo de locaciones.
- `GET /api/v1/personas` - directorio de personas que pueden registrar movimientos.
- `POST /api/v1/movimientos` - registra ingresos, traspasos, usos o ajustes validando reglas de negocio.
- `GET /api/v1/movimientos` - lista todos los movimientos con filtros opcionales por producto, locacion o tipo.
- `GET /api/v1/movimientos/producto/{producto_id}` - kardex de un producto ordenado por fecha descendente.
- `GET /api/v1/stock` - stock consolidado desde la vista `vista_stock_actual` (con filtros opcionales por producto o locacion).
- `GET /api/v1/stock/locaciones` - inventario agrupado por locacion con productos y stock listos para el front.

## Buenas practicas y notas

- SQLAlchemy se ejecuta en modo sincrono para simplificar el MVP; el proyecto esta listo para migrar a async si se requiere.
- Las funciones CRUD encapsulan commits unitarios; envolver varias operaciones en una sola transaccion es responsabilidad de futuras capas de servicio.
- Docker Compose monta `db/schema.sql` en `docker-entrypoint-initdb.d/` para mantener la logica del dominio del lado de PostgreSQL.
- Los errores de base de datos se normalizan a respuestas JSON con mensajes claros para el cliente de la API.
