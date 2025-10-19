from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "DevOps Oracle"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str
    
    # Elasticsearch
    ELASTIC_CLOUD_ID: str
    ELASTIC_API_KEY: str
    ELASTIC_INDEX_NAME: str = "devops-incidents"
    
    # Search settings
    SEARCH_RESULT_LIMIT: int = 10
    KEYWORD_BOOST: float = 1.0
    VECTOR_BOOST: float = 2.0
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()