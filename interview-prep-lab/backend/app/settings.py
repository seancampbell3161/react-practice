"""Runtime configuration, read from the environment (and an optional .env)."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Every knob is LAB_-prefixed so a stray ENV or DATABASE_URL in your
        # shell cannot silently repoint the lab at something else.
        env_prefix="LAB_",
        extra="ignore",
    )

    # docker-compose maps Postgres to host port 5435 and Redis to 6380 so the
    # lab never collides with a locally installed Postgres/Redis.
    database_url: str = "postgresql+asyncpg://lab:lab@localhost:5435/lab"
    test_database_url: str = "postgresql+asyncpg://lab:lab@localhost:5435/lab_test"
    redis_url: str = "redis://localhost:6380/0"

    env: Literal["dev", "test", "prod"] = "dev"

    # Flip to true (LAB_ECHO_SQL=true) to dump every statement SQLAlchemy emits.
    # Pair it with the X-Query-Count header to see *which* queries the count is
    # made of, not just how many.
    echo_sql: bool = False

    # The X-Query-Count response header. On in dev, off in prod — it is a
    # teaching instrument, not a production feature.
    expose_query_count: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
