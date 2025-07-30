from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 應用設定
    app_name: str = "訂閱管理系統"
    debug: bool = True
    
    # 數據庫設定  
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./subscription_db.sqlite")
    
    # JWT 設定
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS 設定
    allowed_origins: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()