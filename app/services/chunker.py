"""
Text chunking with overlap for long documents
"""
from typing import List
from app.config import settings


class TextChunker:
    """Split long text into overlapping chunks"""
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        """
        Initialize chunker with custom or default settings
        
        Args:
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.overlap = overlap or settings.chunk_overlap
        
        if self.overlap >= self.chunk_size:
            raise ValueError("Overlap must be smaller than chunk size")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at sentence/paragraph boundary
            if end < len(text):
                # Look for sentence ending within last 200 chars of chunk
                search_start = max(start, end - 200)
                # Search for period, question mark, or exclamation followed by space
                last_sentence = max(
                    text.rfind('. ', search_start, end),
                    text.rfind('? ', search_start, end),
                    text.rfind('! ', search_start, end),
                    text.rfind('\n\n', search_start, end)
                )
                
                if last_sentence > start:
                    end = last_sentence + 1
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.overlap if end < len(text) else end
        
        return chunks
    
    def get_chunk_info(self, text: str) -> dict:
        """
        Get information about how text would be chunked
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with chunk statistics
        """
        chunks = self.chunk_text(text)
        
        return {
            "total_length": len(text),
            "num_chunks": len(chunks),
            "chunk_size": self.chunk_size,
            "overlap": self.overlap,
            "avg_chunk_length": sum(len(c) for c in chunks) / len(chunks) if chunks else 0
        }
