"""
ChromaDB Manager Service - Singleton pattern for database connection management
"""
import logging
from pathlib import Path
from typing import Optional
import sys

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils import rag_utils as ru


class ChromaDBManager:
    """
    Manages ChromaDB client and collection using singleton pattern.
    Wraps existing rag_utils functions without modifying them.
    """
    
    _instance: Optional['ChromaDBManager'] = None
    _client = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize ChromaDB manager"""
        if not hasattr(self, '_initialized'):
            self.logger = logging.getLogger(__name__)
            self._initialized = True
    
    def get_client(self, db_dir: Optional[str] = None):
        """
        Get or create ChromaDB client.
        Uses existing rag_utils.get_client() function.
        """
        if self._client is None:
            self.logger.info("Initializing ChromaDB client...")
            self._client = ru.get_client(db_dir)
        return self._client
    
    def get_collection(self, collection_name: str = "kb_collection"):
        """
        Get or create ChromaDB collection.
        Uses existing rag_utils.get_collection() function.
        """
        if self._collection is None:
            self.logger.info(f"Getting collection: {collection_name}")
            self._collection = ru.get_collection(collection_name)
        return self._collection
    
    def reset_collection(self):
        """
        Reset the collection by deleting all documents.
        Returns number of documents removed.
        """
        try:
            col = self.get_collection()
            all_docs = col.get(include=["metadatas", "documents"])
            all_ids = [meta.get("id") for meta in all_docs["metadatas"] if "id" in meta]
            
            if all_ids:
                col.delete(ids=all_ids)
                self.logger.info(f"ChromaDB collection cleared. {len(all_ids)} documents removed.")
                return len(all_ids)
            else:
                self.logger.info("Collection is already empty.")
                return 0
        except Exception as e:
            self.logger.exception("Failed to reset ChromaDB collection.")
            raise e


# Singleton instance
chroma_manager = ChromaDBManager()
