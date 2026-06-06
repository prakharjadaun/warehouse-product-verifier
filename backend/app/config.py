from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_LLM_DEPLOYMENT: str = "gpt-4o"
    AZURE_LLM_API_VERSION: str = "2025-01-01-preview"
    SECRET_KEY: str = "changeme"
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
