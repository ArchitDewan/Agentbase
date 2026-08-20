from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentbase API"
    environment: str = "local"
    api_version: str = "0.1.0"
    database_url: str = "postgresql+asyncpg://agentbase:agentbase@localhost:55433/agentbase"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGENTBASE_",
    )


settings = Settings()
