from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # MySQL Database Settings
    mysql_user: str = "root"
    mysql_password: str = "root1234#"  # keep original, will encode in URL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "lms_db"

    @property
    def database_url(self) -> str:
        password = quote_plus(self.mysql_password)  # encode special characters
        return f"mysql+aiomysql://{self.mysql_user}:{password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"

    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Email settings (optional)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # File upload settings
    upload_dir: str = "./uploads"
    max_file_size: int = 5242880

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # ignore DATABASE_URL in .env

settings = Settings()
