from pydantic import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    CACHE_PATH: str = "/tmp/preview_cache"

    class Config:
        env_file = ".env"

settings = Settings()