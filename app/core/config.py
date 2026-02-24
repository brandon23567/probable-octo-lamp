import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Coding Agent"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_agent")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
             self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # We might need to change this as it is suspicious looking ai am i right? 
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    

    SECURE_COOKIES: bool = os.getenv("SECURE_COOKIES", "False").lower() == "true"
    HTTP_ONLY: bool = True
    SAME_SITE: str = "lax"
    DOMAIN: Optional[str] = os.getenv("COOKIE_DOMAIN", None)

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJECTS_DIR: str = os.path.join(BASE_DIR, "projects")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
