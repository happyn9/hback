from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # 🔐 Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # obligatoire en prod
    ALGORITHM: str = "HS256"

    # ⏱ Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REMEMBER_ME_DAYS: int = 30

    # 🗄 Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    OPENAI_API_KEY: str = Field(...,env="OPENAI_API_KEY")

    # ⚙️ App
    DEBUG: bool = False
    SEED_DB: bool = False

    # 📧 SendGrid
    SENDGRID_API_KEY: str = Field(..., env="SENDGRID_API_KEY") 

    class Config:
        env_file = ".env"
        extra = "forbid"

settings = Settings()
