from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    mongodb_uri: str
    mongodb_db_name: str = "govi_netha"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "change_this"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
