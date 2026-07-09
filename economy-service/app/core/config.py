from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/economy_db"
    DB_HOSTS: str = ""
    SENTRY_DSN: str = ""
    JWT_SECRET_KEY: str = "change-me"

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def db_host_list(self) -> list[str]:
        return [h.strip() for h in self.DB_HOSTS.split(",") if h.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
