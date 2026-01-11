"""
Base Agent class for CrewAI agents
"""
from crewai import Agent

class BaseAgent:
    """Base class for all BenchCraft agents"""
    
    def __init__(self, role: str, goal: str, backstory: str, tools: list = None):
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools or [],
            verbose=True,
            allow_delegation=False
        )
