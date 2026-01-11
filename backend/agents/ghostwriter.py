"""
The Ghostwriter Agent - Resume Tailoring
Generates client-specific bio PDFs
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
import google.genai as genai
from config import Config

class GhostwriterAgent(BaseAgent):
    """The Ghostwriter - Content Agent"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        # Configure Gemini API
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = self.client.models.get('gemini-pro')
        super().__init__(
            role="Resume Ghostwriter",
            goal="Create client-specific bio PDFs highlighting relevant industry experience",
            backstory="You are an expert at tailoring resumes and bios to emphasize relevant experience for specific clients and industries."
        )
    
    def generate_tailored_bio(self, emp_id: int, client_industry: str) -> str:
        """
        Generate a tailored bio for a specific client industry
        Returns markdown-formatted bio
        """
        employee = self.db_tool.get_employee(emp_id)
        if not employee:
            return "Employee not found"
        
        # Get employee's project history
        project_history = []
        for allocation in employee.allocations:
            if allocation.project:
                project_history.append({
                    'client': allocation.project.client_name,
                    'project': allocation.project.project_name,
                    'description': allocation.project.description
                })
        
        # Build context
        context = f"""
        Employee Bio Summary: {employee.bio_summary}
        Role Level: {employee.role_level.value if employee.role_level else 'N/A'}
        Skills: {', '.join([s.skill_name for s in employee.skills])}
        Project History: {str(project_history)}
        
        Target Industry: {client_industry}
        """
        
        # Use Gemini to generate tailored bio
        system_prompt = "You are an expert resume writer specializing in tailoring bios for specific industries."
        prompt = f"""
        {system_prompt}
        
        Rewrite the following employee bio to emphasize experience relevant to the {client_industry} industry.
        Highlight any projects, skills, or achievements that would be particularly valuable for {client_industry} clients.
        Keep it professional and concise (2-3 paragraphs).
        
        {context}
        """
        
        try:
            response = self.model.generate_content(
                contents=prompt,
                config={"temperature": 0.7}
            )
            return response.text
        except Exception as e:
            return f"Error generating bio: {str(e)}"
