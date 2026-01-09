from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router as api_router_v1
from app.api.v2 import api_router as api_router_v2
from app.core.config import settings

app = FastAPI(title=settings.project_name)

# Configurar CORS para permitir peticiones desde el frontend
# Usa la configuración para los orígenes permitidos en CORS
allowed_origins = getattr(settings, "allowed_origins", [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permite solo los métodos necesarios
    allow_headers=["*"],  # Permite todos los headers
)

app.include_router(api_router_v2, prefix=settings.api_v2_str)
if settings.enable_v1:
    app.include_router(api_router_v1, prefix=settings.api_v1_str)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Inventario MVP OK"}
