from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from functools import lru_cache
import os

from app.core.config import get_settings
from app.db.models import Base

settings = get_settings()

# Get database URL from environment or settings
def get_database_url() -> str:
    """Get database URL - prioritize DATABASE_URL env var for production"""
    # Check for DATABASE_URL env var first (used by Render)
    db_url = os.environ.get('DATABASE_URL', settings.DATABASE_URL)
    
    # Fix Render's postgres:// URL to work with SQLAlchemy
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif db_url.startswith('postgresql://') and '+psycopg2' not in db_url:
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    return db_url

# Create SQLAlchemy engine
engine = create_engine(get_database_url())

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database() -> Session:
    """
    Dependency function to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()