"""
The Matchmaker Agent - PII Guard & Anonymization
Ensures blind allocation fairness
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
from typing import List, Dict
import re

class MatchmakerAgent(BaseAgent):
    """The Matchmaker - Fairness Agent"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        super().__init__(
            role="Fairness Matchmaker",
            goal="Anonymize employee data to ensure blind, merit-based allocation",
            backstory="You are responsible for maintaining fairness in the allocation process by masking PII until allocation is confirmed."
        )
    
    def anonymize_employee(self, employee) -> Dict:
        """Transform employee data to anonymized format"""
        uuid_short = employee.uuid[-4:] if len(employee.uuid) >= 4 else employee.uuid
        
        # Redact bio summary (remove gendered pronouns if possible)
        bio_redacted = self._redact_bio(employee.bio_summary or "")
        
        return {
            'uuid': employee.uuid,
            'candidate_id': f"Candidate #{uuid_short}",
            'role_level': employee.role_level.value if employee.role_level else None,
            'base_location': employee.base_location,
            'remote_pref': employee.remote_pref,
            'status': employee.status.value if employee.status else None,
            'bio_summary': bio_redacted,
            'skills': [
                {
                    'skill_name': skill.skill_name,
                    'proficiency': skill.proficiency
                }
                for skill in employee.skills
            ]
        }
    
    def _redact_bio(self, bio: str) -> str:
        """Remove gendered pronouns and PII from bio"""
        # Simple redaction - remove common pronouns
        pronouns = ['he', 'she', 'his', 'her', 'him', 'himself', 'herself']
        words = bio.split()
        redacted = [w for w in words if w.lower() not in pronouns]
        return ' '.join(redacted)
    
    def anonymize_search_results(self, emp_ids: List[int], match_scores: Dict[int, float]) -> List[Dict]:
        """Anonymize a list of employees from search results"""
        employees = self.db_tool.get_employees_by_ids(emp_ids)
        anonymized = []
        
        for emp in employees:
            if emp.id in match_scores:
                profile = self.anonymize_employee(emp)
                profile['match_score'] = match_scores[emp.id]
                anonymized.append(profile)
        
        return anonymized
