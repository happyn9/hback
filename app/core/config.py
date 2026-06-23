from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # 🔐 Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"

    # ⏱ Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REMEMBER_ME_DAYS: int = 30

    # 🗄 Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # ⚙️ App
    DEBUG: bool = False
    SEED_DB: bool = False

    # 📧 SendGrid
    SENDGRID_API_KEY: str = Field(..., env="SENDGRID_API_KEY")

    # 💳 Flutterwave — AJOUT
    FLUTTERWAVE_SECRET_KEY: str = Field(..., env="FLUTTERWAVE_SECRET_KEY")
    FRONTEND_URL: str = Field(default="http://localhost:5173", env="FRONTEND_URL")
    BACKEND_URL: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    FLUTTERWAVE_WEBHOOK_HASH: str = Field(..., env="FLUTTERWAVE_WEBHOOK_HASH")

    class Config:
        env_file = ".env"
        extra = "ignore"   

settings = Settings()
