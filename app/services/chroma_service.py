"""
ChromaDB service for vector database operations
"""
import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class ChromaDBService:
    """Service for managing ChromaDB vector database operations"""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model"""
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(settings.chroma_dir)
            ))
            
            # Load embedding model
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            
            # Get or create collection
            self.collection_name = settings.chroma_collection_name
            self.collection = self._get_or_create_collection()
            
            logger.info(f"ChromaDB initialized successfully with collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Customer information database"}
            )
            logger.info(f"Collection '{self.collection_name}' ready with {collection.count()} documents")
            return collection
        except Exception as e:
            logger.error(f"Error accessing collection: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def add_customer(self, customer_id: str, customer_data: Dict, metadata: Dict = None) -> bool:
        """
        Add or update customer document in ChromaDB
        
        Args:
            customer_id: Unique customer identifier
            customer_data: Dictionary with customer information
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            # Create text representation of customer data
            customer_text = self._format_customer_text(customer_data)
            
            # Generate embedding
            embedding = self.generate_embedding(customer_text)
            
            # Prepare metadata
            doc_metadata = {
                "customer_id": customer_id,
                "type": "customer",
                **(metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                ids=[customer_id],
                embeddings=[embedding],
                documents=[customer_text],
                metadatas=[doc_metadata]
            )
            
            logger.info(f"Added customer {customer_id} to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error adding customer {customer_id}: {str(e)}")
            return False
    
    def _format_customer_text(self, customer_data: Dict) -> str:
        """Format customer data as text for embedding"""
        parts = []
        
        if "customer_id" in customer_data:
            parts.append(f"Customer ID: {customer_data['customer_id']}")
        if "name" in customer_data:
            parts.append(f"Name: {customer_data['name']}")
        if "email" in customer_data:
            parts.append(f"Email: {customer_data['email']}")
        if "phone" in customer_data:
            parts.append(f"Phone: {customer_data['phone']}")
        if "address" in customer_data:
            parts.append(f"Address: {customer_data['address']}")
        if "company" in customer_data:
            parts.append(f"Company: {customer_data['company']}")
        if "purchase_history" in customer_data:
            parts.append(f"Purchase History: {customer_data['purchase_history']}")
        if "notes" in customer_data:
            parts.append(f"Notes: {customer_data['notes']}")
        if "status" in customer_data:
            parts.append(f"Status: {customer_data['status']}")
        
        return "\\n".join(parts)
    
    def search_by_customer_id(self, customer_id: str) -> Optional[Dict]:
        """
        Search for customer by ID
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Customer data if found, None otherwise
        """
        try:
            # Try to get document by ID
            result = self.collection.get(
                ids=[customer_id],
                include=["documents", "metadatas"]
            )
            
            if result and result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for customer {customer_id}: {str(e)}")
            return None
    
    def semantic_search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Perform semantic search for customers
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching customer documents
        """
        try:
            if top_k is None:
                top_k = settings.rag_top_k
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def get_all_customers(self, limit: int = None) -> List[Dict]:
        """
        Get all customers from database
        
        Args:
            limit: Maximum number of customers to return
            
        Returns:
            List of customer documents
        """
        try:
            result = self.collection.get(
                include=["documents", "metadatas"],
                limit=limit
            )
            
            customers = []
            if result and result["ids"]:
                for i in range(len(result["ids"])):
                    customers.append({
                        "id": result["ids"][i],
                        "document": result["documents"][i],
                        "metadata": result["metadatas"][i]
                    })
            
            logger.info(f"Retrieved {len(customers)} customers")
            return customers
            
        except Exception as e:
            logger.error(f"Error getting all customers: {str(e)}")
            return []
    
    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete customer by ID
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[customer_id])
            logger.info(f"Deleted customer {customer_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting customer {customer_id}: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_customers": count,
                "embedding_model": settings.embedding_model
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    def health_check(self) -> bool:
        """Check if ChromaDB is healthy"""
        try:
            self.collection.count()
            return True
        except:
            return False
