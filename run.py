#!/usr/bin/env python3
"""
Run the FastAPI application
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("=" * 60)
    print("🚀 SlayFashion Backend API")
    print("=" * 60)
    print(f"📍 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"📦 Shopify Store: {settings.shopify_store_domain}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

