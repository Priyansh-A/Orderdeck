from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    
    SECRET_KEY: str 
    
    ESEWA_MERCHANT_CODE: str = "EPAYTEST"
    ESEWA_SECRET_KEY: str = "8gBm/:&EnhH.1/q"
    ESEWA_BASE_URL: str = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
    ESEWA_SUCCESS_URL: str = "http://localhost:8000/payments/esewa/success"
    ESEWA_FAILURE_URL: str = "http://localhost:8000/payments/esewa/failure"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()