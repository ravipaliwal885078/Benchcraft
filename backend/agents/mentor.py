"""
The Mentor Agent - Training & Career Path Recommendations
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
from typing import List, Dict

class MentorAgent(BaseAgent):
    """The Mentor - Growth Agent"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        super().__init__(
            role="Career Mentor",
            goal="Recommend training paths to help employees match project requirements",
            backstory="You are an expert career advisor who analyzes skill gaps and recommends targeted training to improve project match rates."
        )
    
    def recommend_training(self, emp_id: int, target_project_id: int) -> Dict:
        """
        Recommend training to improve match for a project
        Returns training recommendations
        """
        employee = self.db_tool.get_employee(emp_id)
        project = self.db_tool.get_project(target_project_id)
        
        if not employee or not project:
            return {'error': 'Employee or project not found'}
        
        # Extract required skills from project description/tech_stack
        required_skills = []
        if project.tech_stack:
            required_skills = [s.strip() for s in project.tech_stack.split(',')]
        
        # Get employee's current skills
        employee_skills = {skill.skill_name.lower(): skill.proficiency for skill in employee.skills}
        
        # Find gaps
        gaps = []
        for skill in required_skills:
            skill_lower = skill.lower()
            if skill_lower not in employee_skills or employee_skills[skill_lower] < 4:
                gaps.append({
                    'skill': skill,
                    'current_proficiency': employee_skills.get(skill_lower, 0),
                    'recommended_training': f"{skill} Certification Course"
                })
        
        return {
            'employee_id': emp_id,
            'project_id': target_project_id,
            'current_match': '70%',  # Simplified
            'target_match': '100%',
            'training_recommendations': gaps
        }
