#!/usr/bin/env python3
"""
RAG Setup Script - Downloads PubMed CSV and ingests into ChromaDB
Designed to run safely on startup without crashing the main application
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("setup_rag")

# Google Drive folder containing the CSV
GDRIVE_FOLDER_ID = "1dNL2RnnGKVEsTP8vSC7_E32tnfZW0P04"
CSV_FILENAME = "pubmed_ml_data_2014_2023.csv"
DOWNLOAD_PATH = "/app/app/rag/pubmed_ml_data_2014_2023.csv"
COLLECTION_NAME = "pubmed_rag"


def check_collection_exists():
    """Check if the ChromaDB collection already exists"""
    try:
        from app.rag.retriever import get_chroma_client
        client = get_chroma_client()
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        return COLLECTION_NAME in collection_names
    except Exception as e:
        logger.warning(f"Could not check collection: {e}")
        return False


def download_csv():
    """Download CSV from Google Drive using gdown"""
    try:
        import gdown
        
        # If file already exists and has content, skip download
        if os.path.exists(DOWNLOAD_PATH) and os.path.getsize(DOWNLOAD_PATH) > 1000:
            logger.info(f"✅ CSV already exists at {DOWNLOAD_PATH}")
            return True
        
        logger.info(f"📥 Downloading CSV from Google Drive folder...")
        
        # Download from folder - gdown will find the file
        url = f"https://drive.google.com/drive/folders/{GDRIVE_FOLDER_ID}"
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(DOWNLOAD_PATH), exist_ok=True)
        
        # Download the specific file from the folder
        # Using gdown's folder download with specific file
        gdown.download_folder(url, output=os.path.dirname(DOWNLOAD_PATH), quiet=False)
        
        # Check if file was downloaded
        if os.path.exists(DOWNLOAD_PATH) and os.path.getsize(DOWNLOAD_PATH) > 1000:
            logger.info(f"✅ CSV downloaded successfully: {DOWNLOAD_PATH}")
            return True
        else:
            # Try alternative download method - direct file download
            logger.info("Trying alternative download method...")
            # Sometimes the file ends up with a different path after folder download
            potential_paths = [
                f"/app/app/rag/{CSV_FILENAME}",
                f"/app/{CSV_FILENAME}",
                f"/app/app/rag/pubmed_ml_data_2014_2023/{CSV_FILENAME}",
            ]
            for path in potential_paths:
                if os.path.exists(path):
                    logger.info(f"Found CSV at: {path}")
                    if path != DOWNLOAD_PATH:
                        import shutil
                        shutil.move(path, DOWNLOAD_PATH)
                    return True
            
            logger.error("❌ CSV download failed - file not found after download")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to download CSV: {e}")
        return False


def run_ingestion():
    """Run the PubMed CSV ingestion"""
    try:
        from app.rag.ingest import ingest_pubmed_csv
        
        logger.info("📚 Starting PubMed data ingestion...")
        
        num_chunks = ingest_pubmed_csv(DOWNLOAD_PATH)
        
        logger.info(f"✅ Ingestion complete! {num_chunks} chunks stored in ChromaDB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        return False


def main():
    """Main setup function - safe to run on every startup"""
    logger.info("🚀 RAG Setup Script Starting...")
    
    # Check if collection already exists
    if check_collection_exists():
        logger.info("✅ PubMed RAG collection already exists - skipping setup")
        return 0
    
    logger.info("📝 Collection not found - starting RAG setup...")
    
    # Download CSV
    if not download_csv():
        logger.warning("⚠️ Could not download CSV - RAG will be unavailable")
        return 1
    
    # Run ingestion
    if not run_ingestion():
        logger.warning("⚠️ Ingestion failed - RAG will be unavailable")
        return 1
    
    logger.info("🎉 RAG Setup Complete!")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"❌ RAG Setup crashed: {e}")
        # Exit with 0 to not block app startup
        sys.exit(0)
