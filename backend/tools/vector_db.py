"""
ChromaDB Interface for Vector Search
"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict
import google.genai as genai
from config import Config

class ChromaSearchTool:
    """Tool for semantic search in ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=Config.CHROMA_COLLECTION_NAME
        )
        # Configure Gemini API
        self.client_genai = genai.Client(api_key=Config.GEMINI_API_KEY)
    
    def get_embedding(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """Generate embedding for text using Gemini"""
        result = self.client_genai.models.embed_content(
            model="models/text-embedding-004",
            contents=text,
            config={"task_type": task_type}
        )
        # Handle the response structure of the new SDK
        return result.embeddings[0].values
    
    def add_employee_embedding(self, emp_id: int, bio: str):
        """Add employee bio to vector store"""
        embedding = self.get_embedding(bio)
        self.collection.add(
            ids=[f"emp_{emp_id}"],
            embeddings=[embedding],
            documents=[bio],
            metadatas=[{"emp_id": emp_id}]
        )
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Semantic search for employees matching query
        Returns list of dicts with emp_id and distance
        """
        query_embedding = self.get_embedding(query, task_type="retrieval_query")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        matches = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, emp_id_str in enumerate(results['ids'][0]):
                emp_id = int(emp_id_str.replace('emp_', ''))
                distance = results['distances'][0][i] if results['distances'] else 0
                matches.append({
                    'emp_id': emp_id,
                    'distance': distance,
                    'match_score': 1 - distance  # Convert distance to similarity
                })
        
        return matches