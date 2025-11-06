from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(title=settings.project_name)
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Inventario MVP OK"}
