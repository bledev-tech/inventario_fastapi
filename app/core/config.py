from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Inventario FastAPI MVP"
    api_v1_str: str = "/api/v1"
    api_v2_str: str = "/api/v2"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/inventario"
    secret_key: str = "CHANGE_ME"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    allow_user_signup: bool = True
    enable_v1: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
