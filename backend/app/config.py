from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres123"
    POSTGRES_DB: str = "fastapi"
    POSTGRES_HOST: str = "localhost"
    # POSTGRES_PORT: int = 5432

    SECRET_KEY: str 
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
    )

    @property
    def database_url(self) -> str:
        base_url = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        
        return base_url
    

settings = Settings()