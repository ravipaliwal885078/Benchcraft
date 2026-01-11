"""
The Scout Agent - Semantic Search Engine
Discovers employees matching job descriptions
"""
from agents.base_agent import BaseAgent
from tools.vector_db import ChromaSearchTool

class ScoutAgent(BaseAgent):
    """The Scout - Discovery Agent"""
    
    def __init__(self):
        self.vector_tool = ChromaSearchTool()
        super().__init__(
            role="Talent Scout",
            goal="Find the best matching employees for job descriptions using semantic search",
            backstory="You are an expert at understanding job requirements and matching them to employee profiles using advanced vector search technology."
        )
    
    def search(self, query: str, min_proficiency: int = 1, max_results: int = 10) -> list:
        """
        Search for employees matching the query
        Returns list of emp_ids with match scores
        """
        results = self.vector_tool.search(query, top_k=max_results)
        return results
