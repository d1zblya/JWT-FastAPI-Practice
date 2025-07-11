from pathlib import Path
from typing import List, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

load_dotenv()


class DBSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def database_url(self):
        return (f"postgresql+asyncpg://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")


class AuthSettings(BaseSettings):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    @property
    def private_key(self) -> str:
        """Получить приватный ключ"""
        return self.PRIVATE_KEY_PATH.read_text()

    @property
    def public_key(self) -> str:
        """Получить публичный ключ"""
        return self.PUBLIC_KEY_PATH.read_text()


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8001",
        "http://localhost:8000",
        "http://localhost:8089",
        "http://localhost:5173"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
