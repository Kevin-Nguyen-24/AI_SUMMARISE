"""
Ollama API client for LLM inference
"""
import requests
import logging
from typing import Optional
from app.config import settings


logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = None, model: str = None, timeout: int = None):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.generate_endpoint = f"{self.base_url}/api/generate"
    
    def generate(self, prompt: str, max_retries: int = 1, system_message: str = None) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: Input prompt for the model
            max_retries: Number of retry attempts on failure
            system_message: Optional system message to guide model behavior
            
        Returns:
            Generated text
            
        Raises:
            Exception: If generation fails after retries
        """
        # Get temperature from settings, default to 0.7 for human-like output
        from app.config import settings
        temperature = getattr(settings, 'summary_temperature', 0.7)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,  # Configurable temperature for natural writing
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,  # Reduce repetition
                "num_predict": 512,  # Allow longer, more detailed responses
            }
        }
        
        # Add system message if provided for better context
        if system_message:
            payload["system"] = system_message
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Calling Ollama API (attempt {attempt + 1}/{max_retries + 1})")
                
                response = requests.post(
                    self.generate_endpoint,
                    json=payload,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                if not generated_text:
                    raise ValueError("Empty response from Ollama")
                
                logger.info(f"Successfully generated {len(generated_text)} characters")
                return generated_text
                
            except requests.exceptions.Timeout as e:
                last_error = f"Request timeout after {self.timeout}s"
                logger.warning(f"{last_error} (attempt {attempt + 1})")
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(f"{last_error} (attempt {attempt + 1})")
                
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP error: {e.response.status_code}"
                logger.warning(f"{last_error} (attempt {attempt + 1})")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Error: {last_error} (attempt {attempt + 1})")
        
        raise Exception(f"Failed to generate text after {max_retries + 1} attempts: {last_error}")
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def list_models(self) -> list:
        """
        List available models in Ollama
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
