"""
Configuration settings for BenchCraft AI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / '.env')

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{Path(__file__).parent.parent}/data/benchcraft.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ChromaDB
    CHROMA_DB_PATH = os.getenv(
        'CHROMA_DB_PATH',
        str(Path(__file__).parent.parent / 'data' / 'chroma_store')
    )
    CHROMA_COLLECTION_NAME = 'consultant_vectors'
    
    # Google Gemini API (for embeddings and LLM)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Secret Key
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
