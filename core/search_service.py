"""
Search service using FAISS for semantic similarity search
"""
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple

import faiss

from .models import NoteItem, SearchResult
from .database_service import DatabaseService

class SearchService:
    """Central search service for semantic similarity search"""
    
    def __init__(self, 
                 index_path: str = "faiss.index",
                 embed_dim: int = 768):
        self.index_path = Path(index_path)
        self.embed_dim = embed_dim
        self.index = self._load_or_create_index()
    
    def _load_or_create_index(self) -> faiss.Index:
        """Load existing index or create new one"""
        if self.index_path.exists():
            try:
                return faiss.read_index(str(self.index_path))
            except:
                pass
        
        # Create new index
        base_index = faiss.IndexFlatIP(self.embed_dim)  # Inner product for cosine similarity
        return faiss.IndexIDMap(base_index)
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors for cosine similarity"""
        vectors = vectors.astype("float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms
    
    def add_item(self, item_id: int, embedding: List[float]):
        """Add item embedding to index"""
        vector = np.array([embedding], dtype="float32")
        vector = self._normalize_vectors(vector)
        
        self.index.add_with_ids(vector, np.array([item_id], dtype="int64"))
        self._save_index()
    
    def remove_item(self, item_id: int):
        """Remove item from index"""
        try:
            self.index.remove_ids(np.array([item_id], dtype="int64"))
            self._save_index()
        except:
            pass  # Item might not be in index
    
    def search_similar(self, 
                      query_embedding: List[float],
                      db_service: DatabaseService,
                      top_k: int = 10,
                      similarity_threshold: float = 0.6) -> List[SearchResult]:
        """Search for similar items"""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query vector
        query_vector = np.array([query_embedding], dtype="float32")
        query_vector = self._normalize_vectors(query_vector)
        
        # Search
        similarities, indices = self.index.search(query_vector, top_k + 1)
        
        results = []
        for similarity, idx in zip(similarities[0], indices[0]):
            if idx != -1 and similarity >= similarity_threshold:
                item = db_service.get_item(int(idx))
                if item:
                    results.append(SearchResult(
                        item=item,
                        similarity_score=float(similarity)
                    ))
        
        return results
    
    def _save_index(self):
        """Save index to file"""
        try:
            faiss.write_index(self.index, str(self.index_path))
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def rebuild_index(self, db_service: DatabaseService, ai_service):
        """Rebuild the entire search index"""
        # Create new index
        base_index = faiss.IndexFlatIP(self.embed_dim)
        self.index = faiss.IndexIDMap(base_index)
        
        # Get all items
        items = db_service.get_all_items()
        
        if not items:
            self._save_index()
            return
        
        # Generate embeddings for all items
        texts = [item.enhanced_content for item in items]
        item_ids = [item.id for item in items]
        
        try:
            embeddings = ai_service.generate_embeddings(texts)
            
            # Add to index
            vectors = np.array(embeddings, dtype="float32")
            vectors = self._normalize_vectors(vectors)
            ids = np.array(item_ids, dtype="int64")
            
            self.index.add_with_ids(vectors, ids)
            self._save_index()
            
        except Exception as e:
            print(f"Error rebuilding index: {e}")
    
    def get_stats(self) -> dict:
        """Get index statistics"""
        return {
            "total_items": self.index.ntotal,
            "dimension": self.embed_dim,
            "index_exists": self.index_path.exists()
        }
