import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from .chunker import chunk_pubmed_texts
from .embedder import embed_chunks
from .retriever import store_pubmed_embeddings
import os

def ingest_pubmed_csv(csv_path: str = None) -> int:
    """
    Ingest PubMed papers from CSV format.
    Required columns: title, abstract
    Optional columns: pubmed_id (if missing, will use row index)
    """
    try:
        # Use environment variable if csv_path is not provided
        if csv_path is None:
            csv_path = os.getenv("PUBMED_CSV_PATH", "backend/rag/pubmed_ml_data_2014_2023.csv")

        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        if 'title' not in df.columns or 'abstract' not in df.columns:
            raise ValueError("CSV must contain 'title' and 'abstract' columns")
        
        # Handle missing pubmed_id column
        if 'pubmed_id' not in df.columns:
            df['pubmed_id'] = df.index.astype(str)
        
        # Process each paper
        documents = []
        for idx, row in df.iterrows():
            # Handle NaN values
            title = str(row['title']) if pd.notna(row['title']) else ""
            abstract = str(row['abstract']) if pd.notna(row['abstract']) else ""
            pubmed_id = str(row['pubmed_id']) if pd.notna(row['pubmed_id']) else str(idx)
            
            # Skip if both title and abstract are empty
            if not title and not abstract:
                continue
                
            # Combine title and abstract
            combined_text = f"{title}. {abstract}".strip()
            
            documents.append({
                'text': combined_text,
                'title': title,
                'abstract': abstract,
                'pubmed_id': pubmed_id,
                'source_row': idx
            })
        
        # Chunk the documents
        chunks = chunk_pubmed_texts(documents)
        
        # Create embeddings
        embeddings_with_metadata = embed_chunks(chunks)
        
        # Store in ChromaDB
        store_pubmed_embeddings(embeddings_with_metadata)
        
        return len(chunks)
        
    except Exception as e:
        raise Exception(f"Error ingesting PubMed CSV: {str(e)}")

def ingest_documents(file_paths: List[str]):
    """Legacy function for backward compatibility"""
    # For now, assume it's a CSV if single file
    if len(file_paths) == 1 and file_paths[0].endswith('.csv'):
        return ingest_pubmed_csv(file_paths[0])
    else:
        raise NotImplementedError("Only PubMed CSV ingestion is currently supported")
