from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./slayfashion.db"
    
    # Shopify
    shopify_store_domain: str
    shopify_admin_api_token: str
    shopify_storefront_access_token: str
    shopify_api_version: str = "2024-10"
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 10080  # 7 days
    
    # OTP
    otp_expiration_minutes: int = 10
    otp_length: int = 6
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

