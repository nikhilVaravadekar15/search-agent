import logging
from urllib.parse import quote_plus

from pydantic import computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # debug
    DEBUG: bool = False
    LOGGING_LEVEL: int = logging.INFO

    # cors middleware
    FRONTEND_URL: str

    # Chat model
    API_KEY: str
    LLM_MODEL: str = "openai/gpt-oss:20b"
    MODEL_URL: str = "http://localhost:11434/v1"
    MODEL_TEMPERATURE: float = 0
    MAX_OUTPUT_TOKENS: int = 8192

    # Tools calling limit
    TOOL_CALLING_LIMIT: int = 32
    SUMMERIZATION_MIDDLEWARE_LIMIT: float = 0.7
    # Data staging limits
    MAX_DOCUMENTS_STAGING_LIMIT: int = 10

    # database
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432

    @computed_field
    def db_url(self) -> str:
        """
        use this for alembic
        """
        password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql+psycopg://{self.DATABASE_USERNAME}:{password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @computed_field
    def async_db_url(self) -> str:
        """
        use this for fastapi
        """
        password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql+asyncpg://{self.DATABASE_USERNAME}:{password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug(cls, v: any) -> bool:
        """Validate and convert DEBUG to boolean"""
        if isinstance(v, str):
            if v.lower() in ("True", "true", "1", "yes", "on"):
                return True
            elif v.lower() in ("False", "false", "0", "no", "off"):
                return False
            else:
                raise ValueError(f"Invalid DEBUG value: {v}")
        if isinstance(v, bool):
            return v
        if isinstance(v, int):
            return bool(v)
        raise ValueError(f"Invalid DEBUG value: {v}")

    @field_validator("LOGGING_LEVEL", mode="before")
    @classmethod
    def validate_logging_level(cls, v: any) -> int:
        """Validate LOGGING_LEVEL format"""
        if isinstance(v, str):
            level = logging._nameToLevel.get(v.upper())
            if level is not None:
                return level
            raise ValueError(f"Invalid log level: {v}")
        if isinstance(v, int):
            return v
        raise ValueError(f"Invalid log level: {v}")

    @model_validator(mode="after")
    def set_logging_level_from_debug(self) -> "Settings":
        """Automatically set LOGGING_LEVEL based on DEBUG"""

        if self.LOGGING_LEVEL == logging.INFO and self.DEBUG:
            self.LOGGING_LEVEL = logging.DEBUG
        elif self.LOGGING_LEVEL == logging.DEBUG and not self.DEBUG:
            self.LOGGING_LEVEL = logging.INFO
        return self

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
