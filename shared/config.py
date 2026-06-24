from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/inventory"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8765


settings = Settings()
