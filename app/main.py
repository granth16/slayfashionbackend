from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routers import auth, customer
from .config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    print("🚀 Starting SlayFashion Backend API...")
    print(f"📦 Shopify Store: {settings.shopify_store_domain}")
    print(f"📱 Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down SlayFashion Backend API...")


# Create FastAPI app
app = FastAPI(
    title="SlayFashion Backend API",
    description="OTP-based authentication for Shopify using the bridge method (GoKwik/KwikPass approach)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(customer.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SlayFashion Backend API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "description": "OTP-based Shopify authentication using the bridge method"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "shopify_configured": bool(settings.shopify_store_domain and settings.shopify_admin_api_token)
    }

