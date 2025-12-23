"""
AI Summarization Server - Main Application
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.summarize import router as summarize_router
from .services.ollama_client import OllamaClient


# Configure logging
log_file = settings.log_dir / f"server_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="AI Summarization Server",
    description="Local GPU-powered document summarization using Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS middleware for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your security needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(summarize_router, tags=["Summarization"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services and check Ollama connectivity"""
    logger.info("=" * 60)
    logger.info("Starting AI Summarization Server")
    logger.info("=" * 60)
    logger.info(f"Ollama URL: {settings.ollama_base_url}")
    logger.info(f"Model: {settings.ollama_model}")
    logger.info(f"Max file size: {settings.max_file_size_mb}MB")
    logger.info(f"Allowed extensions: {', '.join(settings.allowed_extensions)}")
    
    # Check Ollama health
    ollama = OllamaClient()
    if ollama.health_check():
        logger.info("[OK] Ollama service is healthy")
        
        # List available models
        models = ollama.list_models()
        if models:
            logger.info(f"Available models: {', '.join(models)}")
            if settings.ollama_model not in models:
                logger.warning(f"[WARNING] Configured model '{settings.ollama_model}' not found in available models")
        else:
            logger.warning("[WARNING] No models found in Ollama")
    else:
        logger.error("[ERROR] Ollama service is not available")
        logger.error(f"  Please ensure Ollama is running at {settings.ollama_base_url}")
        logger.error(f"  And the model '{settings.ollama_model}' is installed")
    
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Summarization Server")


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with server information"""
    return {
        "service": "AI Summarization Server",
        "status": "running",
        "version": "1.0.0",
        "model": settings.ollama_model,
        "endpoints": {
            "summarize": "/summarize",
            "health": "/health",
            "docs": "/docs"
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns server and Ollama status
    """
    ollama = OllamaClient()
    ollama_healthy = ollama.health_check()
    
    return {
        "server": "healthy",
        "ollama": "healthy" if ollama_healthy else "unhealthy",
        "ollama_url": settings.ollama_base_url,
        "model": settings.ollama_model
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level=settings.log_level.lower()
    )
