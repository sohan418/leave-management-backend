from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # MySQL Database Settings (picked from .env)
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    mysql_db: str

    @property
    def database_url(self) -> str:
        password = quote_plus(self.mysql_password)  # encode special characters
        return f"mysql+aiomysql://{self.mysql_user}:{password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Email settings (optional)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # File upload settings
    upload_dir: str = "./uploads"
    max_file_size: int = 5242880  # 5 MB

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
