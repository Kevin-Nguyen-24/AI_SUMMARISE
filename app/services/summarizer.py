"""
Hierarchical text summarization service
"""
import logging
from typing import List, Tuple
from app.services.ollama_client import OllamaClient
from app.services.chunker import TextChunker


logger = logging.getLogger(__name__)


class Summarizer:
    """Hierarchical text summarization using Ollama"""
    
    # Prompts for different summarization stages - designed for human-like output
    CHUNK_PROMPT = """Read this text and explain what it's about in 2-3 natural sentences, as if you're telling a colleague.

Write in a conversational, human way. Focus on the main points and what stands out. Be brief but clear.

Text:
{text}

Your explanation:"""

    FINAL_PROMPT = """You are an expert at explaining data and documents in natural, conversational language.

Below are summaries of different sections. Write a brief, flowing paragraph (2-4 sentences) that explains what this document is about - as if you're telling a colleague in person.

Write naturally, like a human would speak. Focus on the main story, key patterns, and what stands out. Be concise and engaging.

Section summaries:
{summaries}

Your natural summary (2-4 sentences):"""

    BULLET_PROMPT = """Based on this summary, write 3-5 key insights as short, natural sentences. Each insight should be specific and highlight what matters most.

Write as if you're explaining the highlights to someone. Be concise and direct. Write each insight on a new line starting with '-'.

Summary:
{summary}

Key insights:
"""

    SYSTEM_MESSAGE = "You are a helpful AI assistant. Your goal is to provide concise and accurate information."

    def __init__(self, ollama_client: OllamaClient = None, chunker: TextChunker = None):
        """
        Initialize summarizer
        
        Args:
            ollama_client: Ollama client instance
            chunker: Text chunker instance
        """
        self.ollama = ollama_client or OllamaClient()
        self.chunker = chunker or TextChunker()
    
    def summarize_chunk(self, text: str) -> str:
        """
        Summarize a single chunk of text
        
        Args:
            text: Text chunk to summarize
            
        Returns:
            Summary of the chunk
        """
        prompt = self.CHUNK_PROMPT.format(text=text)
        return self.ollama.generate(prompt)
    
    def summarize_chunks(self, chunks: List[str]) -> List[str]:
        """
        Summarize multiple chunks sequentially
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of chunk summaries
        """
        summaries = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Summarizing chunk {i + 1}/{len(chunks)}")
            summary = self.summarize_chunk(chunk)
            summaries.append(summary)
        
        return summaries
    
    def combine_summaries(self, summaries: List[str]) -> str:
        """
        Combine multiple summaries into a final summary
        
        Args:
            summaries: List of chunk summaries
            
        Returns:
            Final combined summary
        """
        # If only one summary, return it directly
        if len(summaries) == 1:
            return summaries[0]
        
        # Combine summaries with numbering
        combined = "\n\n".join([f"{i+1}. {s}" for i, s in enumerate(summaries)])
        
        prompt = self.FINAL_PROMPT.format(summaries=combined)
        return self.ollama.generate(prompt, system_message=self.SYSTEM_MESSAGE)
    
    def extract_bullet_points(self, summary: str) -> List[str]:
        """
        Extract key points as bullet list from summary
        
        Args:
            summary: Detailed summary text
            
        Returns:
            List of bullet points
        """
        prompt = self.BULLET_PROMPT.format(summary=summary)
        response = self.ollama.generate(prompt, system_message=self.SYSTEM_MESSAGE)
        
        # Parse bullet points from response
        lines = response.strip().split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            # Handle different bullet formats
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                bullets.append(line.lstrip('-•* ').strip())
            elif line and len(bullets) < 5:  # Accept up to 5 points
                bullets.append(line)
        
        # Return top 5 points
        return bullets[:5]
    
    def summarize(self, text: str) -> Tuple[List[str], str]:
        """
        Perform hierarchical summarization on text
        
        Args:
            text: Input text to summarize
            
        Returns:
            Tuple of (bullet_points, detailed_summary)
        """
        logger.info(f"Starting summarization for text of length {len(text)}")
        
        # Step 1: Chunk the text
        chunks = self.chunker.chunk_text(text)
        logger.info(f"Text split into {len(chunks)} chunks")
        
        # Step 2: Summarize each chunk
        chunk_summaries = self.summarize_chunks(chunks)
        
        # Step 3: Combine chunk summaries into final summary
        logger.info("Combining chunk summaries")
        detailed_summary = self.combine_summaries(chunk_summaries)
        
        # Step 4: Extract bullet points
        logger.info("Extracting key points")
        bullet_points = self.extract_bullet_points(detailed_summary)
        
        logger.info("Summarization complete")
        
        return bullet_points, detailed_summary
