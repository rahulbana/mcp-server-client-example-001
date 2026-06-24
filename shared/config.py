from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Server-side ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/inventory"
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8765

    # --- Client-side ---
    # Full URL the client uses to reach the server (may be a remote host)
    mcp_server_url: str = "http://localhost:8765/mcp"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"


settings = Settings()
