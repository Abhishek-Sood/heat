import re
import re
from typing import List, Dict, Any

def estimate_tokens(text: str) -> int:
    """Rough estimation: 1 token ≈ 4 characters for English text"""
    return len(text) // 4

def chunk_pubmed_texts(documents: List[Dict[str, Any]], 
                      target_tokens: int = 400, 
                      overlap_tokens: int = 50) -> List[Dict[str, Any]]:
    """
    Chunk PubMed documents into 300-500 token chunks with overlap.
    
    Args:
        documents: List of documents with 'text', 'title', 'abstract', 'pubmed_id'
        target_tokens: Target tokens per chunk (default 400)
        overlap_tokens: Overlap between chunks (default 50)
    
    Returns:
        List of chunks with metadata
    """
    chunks = []
    
    for doc in documents:
        text = doc['text']
        title = doc['title']
        pubmed_id = doc['pubmed_id']
        
        # If text is short enough, keep as single chunk
        if estimate_tokens(text) <= 500:
            chunks.append({
                'text': text,
                'title': title,
                'pubmed_id': pubmed_id,
                'chunk_id': f"{pubmed_id}_0",
                'chunk_index': 0,
                'total_chunks': 1
            })
            continue
        
        # Split into sentences for better chunking
        sentences = re.split(r'[.!?]+\s+', text)
        
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = estimate_tokens(sentence)
            
            # If adding this sentence would exceed target, finalize current chunk
            if current_tokens + sentence_tokens > target_tokens and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'title': title,
                    'pubmed_id': pubmed_id,
                    'chunk_id': f"{pubmed_id}_{chunk_index}",
                    'chunk_index': chunk_index,
                    'total_chunks': -1  # Will update later
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap_tokens*4:] if len(current_chunk) > overlap_tokens*4 else current_chunk
                current_chunk = overlap_text + " " + sentence
                current_tokens = estimate_tokens(current_chunk)
                chunk_index += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
        
        # Add final chunk if there's remaining text
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'title': title,
                'pubmed_id': pubmed_id,
                'chunk_id': f"{pubmed_id}_{chunk_index}",
                'chunk_index': chunk_index,
                'total_chunks': chunk_index + 1
            })
            
        # Update total_chunks for all chunks of this document
        doc_chunks = [c for c in chunks if c['pubmed_id'] == pubmed_id]
        total_chunks = len(doc_chunks)
        for chunk in doc_chunks:
            chunk['total_chunks'] = total_chunks
    
    return chunks

def chunk_document(docs, chunk_size=1000, chunk_overlap=100):
    """Legacy function for backward compatibility"""
    # This is kept for compatibility with existing code
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)
