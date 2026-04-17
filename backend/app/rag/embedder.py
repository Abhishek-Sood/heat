from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np

class PubMedEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedder with the specified model"""
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts"""
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]

# Global embedder instance
_embedder = None

def get_embedder() -> PubMedEmbedder:
    """Get global embedder instance (singleton pattern)"""
    global _embedder
    if _embedder is None:
        _embedder = PubMedEmbedder()
    return _embedder

def embed_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Embed PubMed chunks and return with metadata.
    
    Args:
        chunks: List of chunks with 'text', 'title', 'pubmed_id', 'chunk_id'
    
    Returns:
        List of chunks with embeddings added
    """
    embedder = get_embedder()
    
    # Extract texts for batch embedding
    texts = [chunk['text'] for chunk in chunks]
    
    # Get embeddings
    embeddings = embedder.embed_batch(texts)
    
    # Add embeddings to chunks
    results = []
    for i, chunk in enumerate(chunks):
        chunk_with_embedding = chunk.copy()
        chunk_with_embedding['embedding'] = embeddings[i]
        results.append(chunk_with_embedding)
    
    return results
