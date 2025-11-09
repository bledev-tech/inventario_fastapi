from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(title=settings.project_name)

# 👇 Orígenes permitidos (frontend)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # agrega otros si usas otro puerto/dominio
]

# 👇 Middleware CORS (tiene que ir antes de include_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # en desarrollo puedes usar ["*"] si quieres soltarte
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],          # Authorization, Content-Type, etc.
)

# Rutas API
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Inventario MVP OK"}
