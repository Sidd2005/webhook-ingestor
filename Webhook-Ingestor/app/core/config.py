from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Use a specific name to avoid conflict with Replit's Postgres DATABASE_URL
    SQLITE_URL: str = "sqlite:///./webhooks.db"
    SECRET_KEY: str = "change_this_secret"
    
    class Config:
        env_file = ".env"

settings = Settings()
