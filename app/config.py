"""
Configuration management for AI Summarization Server
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss:20b"
    ollama_timeout: int = 120
    
    # Server Configuration
    max_file_size_mb: int = 20
    allowed_extensions: List[str] = ["pdf", "docx", "txt", "xlsx", "xls"]
    
    # Chunking Configuration
    chunk_size: int = 3000
    chunk_overlap: int = 300
    
    # ChromaDB Configuration
    chroma_persist_directory: str = "./data/chromadb"
    chroma_collection_name: str = "customers"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # RAG Configuration
    rag_top_k: int = 5
    rag_temperature: float = 0.7
    
    # Summarization Style Configuration
    summary_temperature: float = 0.7  # 0.0-1.0: Higher = more creative/human-like
    summary_style: str = "conversational"  # Options: conversational, formal, casual
    
    # API Configuration
    api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "temp" / "uploads"
    log_dir: Path = base_dir / "logs"
    
    @property
    def data_dir(self) -> Path:
        """Data directory path"""
        return self.base_dir / "data"
    
    @property
    def chroma_dir(self) -> Path:
        """ChromaDB directory path"""
        return Path(self.chroma_persist_directory)
    
    @property
    def customers_data_dir(self) -> Path:
        """Customers data directory path"""
        return self.base_dir / "data" / "customers"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.customers_data_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes"""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()
