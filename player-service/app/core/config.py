from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/player_db"
    ECONOMY_DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/economy_db"
    DB_HOSTS: str = ""
    SENTRY_DSN: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_PLAY_PACKAGE_NAME: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""
    JWT_SECRET_KEY: str = "change-me"
    JWT_EXPIRATION_DAYS: int = 7
    DEV_MODE: bool = False

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def async_economy_database_url(self) -> str:
        return self.ECONOMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def db_host_list(self) -> list[str]:
        return [h.strip() for h in self.DB_HOSTS.split(",") if h.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
