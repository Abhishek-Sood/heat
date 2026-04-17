import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from .embedder import get_embedder
from .prompts import build_rag_context

# ChromaDB configuration
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_data")
COLLECTION_NAME = "pubmed_rag"

def get_chroma_client():
    """Get ChromaDB client with persistent storage"""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def store_pubmed_embeddings(chunks_with_embeddings: List[Dict[str, Any]]) -> None:
    """
    Store PubMed chunks with embeddings in ChromaDB.
    
    Args:
        chunks_with_embeddings: List of chunks with 'embedding', 'text', 'title', 'pubmed_id', 'chunk_id'
    """
    client = get_chroma_client()
    
    # Create or get collection
    try:
        collection = client.get_collection(COLLECTION_NAME)
        # Clear existing data for fresh ingestion
        collection.delete(ids=collection.get()['ids'])
    except ValueError:
        # Collection doesn't exist, create it
        collection = client.create_collection(COLLECTION_NAME)
    
    # Prepare data for ChromaDB
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    
    for chunk in chunks_with_embeddings:
        ids.append(chunk['chunk_id'])
        embeddings.append(chunk['embedding'])
        documents.append(chunk['text'])
        metadatas.append({
            'title': chunk['title'],
            'pubmed_id': chunk['pubmed_id'],
            'chunk_index': chunk.get('chunk_index', 0),
            'total_chunks': chunk.get('total_chunks', 1)
        })
    
    # Add to collection in batches (ChromaDB has size limits)
    batch_size = 1000
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        batch_documents = documents[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]
        
        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas
        )

def retrieve_pubmed_chunks(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve relevant PubMed chunks for a query.
    
    Args:
        query: Search query
        top_k: Number of chunks to retrieve
    
    Returns:
        List of retrieved chunks with metadata
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(COLLECTION_NAME)
        
        # Generate query embedding
        embedder = get_embedder()
        query_embedding = embedder.embed_text(query)
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        retrieved_chunks = []
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            for i in range(len(documents)):
                chunk = {
                    'text': documents[i],
                    'title': metadatas[i]['title'],
                    'pubmed_id': metadatas[i]['pubmed_id'],
                    'chunk_index': metadatas[i]['chunk_index'],
                    'total_chunks': metadatas[i]['total_chunks'],
                    'similarity_score': 1 - distances[i]  # Convert distance to similarity
                }
                retrieved_chunks.append(chunk)
        
        return retrieved_chunks
        
    except Exception as e:
        print(f"Error retrieving PubMed chunks: {str(e)}")
        return []

def get_rag_context(query: str) -> str:
    """
    MANDATORY helper function for LLM endpoint integration.
    
    Args:
        query: User query
        
    Returns:
        Formatted RAG context string with references, or empty string if no relevant docs
    """
    try:
        # Detect if query is medical/research related
        medical_keywords = [
            'medication', 'drug', 'treatment', 'therapy', 'disease', 'condition', 
            'symptom', 'diagnosis', 'clinical', 'study', 'research', 'trial',
            'patient', 'medical', 'health', 'medicine', 'pharmaceutical'
        ]
        
        query_lower = query.lower()
        is_medical_query = any(keyword in query_lower for keyword in medical_keywords)
        
        if not is_medical_query:
            return ""
        
        # Retrieve relevant chunks
        chunks = retrieve_pubmed_chunks(query, top_k=3)
        
        if not chunks:
            return ""
        
        # Use prompts module to build context
        return build_rag_context(query, chunks)
        
    except Exception as e:
        print(f"Error getting RAG context: {str(e)}")
        return ""

# Legacy functions for backward compatibility
def store_embeddings(embeddings):
    """Legacy function for backward compatibility"""
    print("Warning: Using legacy store_embeddings. Use store_pubmed_embeddings instead.")
    pass

def retrieve_medical_knowledge(query: str, top_k: int = 5):
    """Legacy function for backward compatibility"""
    chunks = retrieve_pubmed_chunks(query, top_k)
    documents = [chunk['text'] for chunk in chunks]
    metadatas = [{k: v for k, v in chunk.items() if k != 'text'} for chunk in chunks]
    return {"answer": documents, "sources": metadatas}
