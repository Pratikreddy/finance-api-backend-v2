from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT: str
    AZURE_OPENAI_API_VERSION: str
    
    # Test UUID for development
    TEST_UUID: str = "b4d6f3e2-8c9a-4d2b-9f1e-3a5c7d8e9f1a"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars

settings = Settings()