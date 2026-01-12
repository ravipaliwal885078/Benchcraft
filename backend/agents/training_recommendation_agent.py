"""
Training Recommendation Agent - Upskilling over Hiring
Analyzes project pipeline requirements and employee skills to recommend training
instead of hiring when feasible.
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
from models import Employee, Project, Allocation, EmployeeSkill, EmployeeStatus, ProjectStatus
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import date, timedelta
from typing import List, Dict, Optional
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from config import Config

class TrainingRecommendationAgent(BaseAgent):
    """The Training Recommendation Agent - Upskilling Strategist"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        # Configure Gemini API for AI insights
        if Config.GEMINI_API_KEY and genai:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Warning: Could not configure Gemini API: {e}")
                self.model = None
        else:
            self.model = None
        
        super().__init__(
            role="Training & Upskilling Strategist",
            goal="Recommend upskilling existing employees over hiring new ones by identifying skill gaps in upcoming projects and suggesting targeted training",
            backstory="You are an expert talent development strategist who analyzes project pipeline requirements, current employee skills, and availability to recommend cost-effective training programs. You prioritize upskilling over hiring to reduce costs, improve employee retention, and accelerate project readiness."
        )
    
    def analyze_skill_gaps_and_recommend_training(self) -> Dict:
        """
        Main method: Analyze upcoming projects and recommend training for existing employees
        Returns comprehensive recommendations with cost savings and benefits
        """
        session = self.db_tool.Session()
        try:
            # Get upcoming projects (PIPELINE status)
            upcoming_projects = session.query(Project).filter(
                Project.status == ProjectStatus.PIPELINE,
                Project.probability >= 50  # Only consider projects with reasonable probability
            ).all()
            
            if not upcoming_projects:
                return {
                    'recommendations': [],
                    'summary': {
                        'total_projects_analyzed': 0,
                        'total_recommendations': 0,
                        'estimated_cost_savings': 0,
                        'estimated_time_savings_days': 0
                    },
                    'message': 'No upcoming projects found in pipeline'
                }
            
            recommendations = []
            total_cost_savings = 0
            total_time_savings = 0
            
            for project in upcoming_projects:
                # Extract required skills from project
                required_skills = self._extract_required_skills(project)
                
                if not required_skills:
                    continue
                
                # Find available employees (not 100% allocated, not on notice)
                available_employees = self._get_available_employees(session)
                
                # For each required skill combination, find best training candidates
                for skill_requirement in required_skills:
                    skill_name = skill_requirement['skill']
                    min_proficiency = skill_requirement.get('min_proficiency', 3)
                    
                    # Find employees who have some related skills but missing this specific one
                    candidates = self._find_training_candidates(
                        session, available_employees, skill_name, min_proficiency, project
                    )
                    
                    for candidate in candidates:
                        recommendation = self._create_training_recommendation(
                            candidate, project, skill_name, skill_requirement
                        )
                        if recommendation:
                            recommendations.append(recommendation)
                            total_cost_savings += recommendation.get('cost_savings', 0)
                            total_time_savings += recommendation.get('time_savings_days', 0)
            
            # Generate AI insights if model available
            ai_insights = self._generate_ai_insights(recommendations) if self.model else None
            
            return {
                'recommendations': recommendations[:20],  # Limit to top 20
                'summary': {
                    'total_projects_analyzed': len(upcoming_projects),
                    'total_recommendations': len(recommendations),
                    'estimated_cost_savings': round(total_cost_savings, 2),
                    'estimated_time_savings_days': total_time_savings
                },
                'ai_insights': ai_insights
            }
        finally:
            session.close()
    
    def _extract_required_skills(self, project: Project) -> List[Dict]:
        """Extract required skills from project description and tech_stack"""
        skills = []
        
        # Extract from tech_stack
        if project.tech_stack:
            tech_skills = [s.strip() for s in project.tech_stack.split(',')]
            for skill in tech_skills:
                if skill:
                    skills.append({
                        'skill': skill,
                        'min_proficiency': 3,  # Default to intermediate
                        'source': 'tech_stack'
                    })
        
        # Extract from description (simple keyword matching)
        if project.description:
            description_lower = project.description.lower()
            # Common skill keywords
            skill_keywords = {
                'python': 'Python',
                'java': 'Java',
                'javascript': 'JavaScript',
                'react': 'React',
                'node.js': 'Node.js',
                'aws': 'AWS',
                'azure': 'Azure',
                'docker': 'Docker',
                'kubernetes': 'Kubernetes',
                'appian': 'Appian',
                'machine learning': 'Machine Learning',
                'data science': 'Data Science',
                'devops': 'DevOps'
            }
            
            for keyword, skill_name in skill_keywords.items():
                if keyword in description_lower and not any(s['skill'] == skill_name for s in skills):
                    # Check if skill requires senior level
                    is_senior = 'senior' in description_lower or 'lead' in description_lower
                    skills.append({
                        'skill': skill_name,
                        'min_proficiency': 4 if is_senior else 3,
                        'source': 'description'
                    })
        
        return skills
    
    def _get_available_employees(self, session) -> List[Employee]:
        """Get employees who are available (not 100% allocated, not on notice)"""
        today = date.today()
        
        # Get all employees
        all_employees = session.query(Employee).options(
            selectinload(Employee.skills),
            selectinload(Employee.allocations)
        ).filter(
            Employee.status != EmployeeStatus.NOTICE_PERIOD
        ).all()
        
        available = []
        for emp in all_employees:
            # Calculate current allocation percentage
            active_allocations = [a for a in emp.allocations if 
                                 (a.end_date is None or a.end_date >= today) and
                                 a.start_date <= today]
            
            total_allocation = sum(
                getattr(a, 'internal_allocation_percentage', getattr(a, 'allocation_percentage', 0) or 0)
                for a in active_allocations
            )
            
            # Consider available if less than 100% allocated
            if total_allocation < 100:
                available.append(emp)
        
        return available
    
    def _find_training_candidates(
        self, 
        session, 
        available_employees: List[Employee], 
        required_skill: str, 
        min_proficiency: int,
        project: Project
    ) -> List[Dict]:
        """Find employees who could be trained for this skill"""
        candidates = []
        
        for emp in available_employees:
            # Get employee's current skills
            employee_skills = {skill.skill_name.lower(): skill.proficiency for skill in emp.skills}
            
            # Check if employee has related skills but missing the required one
            required_skill_lower = required_skill.lower()
            has_skill = required_skill_lower in employee_skills
            current_proficiency = employee_skills.get(required_skill_lower, 0)
            
            # Candidate if:
            # 1. Doesn't have the skill at all, OR
            # 2. Has the skill but below required proficiency
            if not has_skill or current_proficiency < min_proficiency:
                # Check if employee has related/transferable skills
                has_related_skills = self._has_related_skills(employee_skills, required_skill)
                
                # Calculate match score based on existing skills
                match_score = self._calculate_match_score(employee_skills, project, required_skill)
                
                if has_related_skills or match_score > 50:  # At least 50% match
                    candidates.append({
                        'employee': emp,
                        'current_proficiency': current_proficiency,
                        'required_proficiency': min_proficiency,
                        'match_score': match_score,
                        'has_related_skills': has_related_skills
                    })
        
        # Sort by match score (highest first)
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        return candidates[:5]  # Top 5 candidates
    
    def _has_related_skills(self, employee_skills: Dict[str, int], required_skill: str) -> bool:
        """Check if employee has skills related to the required skill"""
        required_lower = required_skill.lower()
        
        # Define skill relationships
        skill_groups = {
            'python': ['python', 'django', 'flask', 'fastapi', 'data science', 'machine learning'],
            'java': ['java', 'spring', 'spring boot', 'j2ee'],
            'javascript': ['javascript', 'react', 'node.js', 'typescript', 'angular', 'vue'],
            'react': ['react', 'javascript', 'typescript', 'frontend'],
            'aws': ['aws', 'cloud', 'devops', 'docker', 'kubernetes'],
            'azure': ['azure', 'cloud', 'devops', 'docker'],
            'appian': ['appian', 'low-code', 'bpm', 'workflow'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'aws', 'azure']
        }
        
        # Check if any related skill exists
        for group_skill, related in skill_groups.items():
            if group_skill in required_lower:
                for related_skill in related:
                    if related_skill in employee_skills and employee_skills[related_skill] >= 3:
                        return True
        
        return False
    
    def _calculate_match_score(self, employee_skills: Dict[str, int], project: Project, required_skill: str) -> float:
        """Calculate how well employee matches the project (0-100)"""
        score = 0.0
        max_score = 100.0
        
        # Extract project tech stack
        if project.tech_stack:
            tech_stack = [s.strip().lower() for s in project.tech_stack.split(',')]
            matching_skills = sum(1 for skill in tech_stack if skill in employee_skills)
            if tech_stack:
                score += (matching_skills / len(tech_stack)) * 40  # 40% weight
        
        # Check domain match
        if project.industry_domain:
            # Simple domain matching (could be enhanced)
            score += 20  # Base domain score
        
        # Check if has related skills to required skill
        if self._has_related_skills(employee_skills, required_skill):
            score += 30  # 30% weight for related skills
        
        # Role level match (could be enhanced)
        score += 10  # Base role level score
        
        return min(score, max_score)
    
    def _create_training_recommendation(
        self, 
        candidate: Dict, 
        project: Project, 
        skill_name: str, 
        skill_requirement: Dict
    ) -> Optional[Dict]:
        """Create a training recommendation with cost/time savings"""
        employee = candidate['employee']
        current_prof = candidate['current_proficiency']
        required_prof = skill_requirement.get('min_proficiency', 3)
        
        # Estimate training cost (simplified - could be enhanced with actual training costs)
        training_cost = self._estimate_training_cost(skill_name, required_prof, current_prof)
        
        # Estimate hiring cost (simplified)
        hiring_cost = self._estimate_hiring_cost(employee.role_level, skill_name)
        
        # Calculate savings
        cost_savings = hiring_cost - training_cost
        
        # Estimate time savings (hiring typically takes 30-60 days, training 7-14 days)
        hiring_time_days = 45  # Average
        training_time_days = 10  # Average
        time_savings = hiring_time_days - training_time_days
        
        # Only recommend if cost savings > 0
        if cost_savings <= 0:
            return None
        
        # Calculate employee utilization
        today = date.today()
        active_allocations = [a for a in employee.allocations if 
                             (a.end_date is None or a.end_date >= today) and
                             a.start_date <= today]
        total_allocation = sum(
            getattr(a, 'internal_allocation_percentage', getattr(a, 'allocation_percentage', 0) or 0)
            for a in active_allocations
        )
        available_capacity = 100 - total_allocation
        
        return {
            'employee_id': employee.id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'employee_role': employee.role_level,
            'employee_email': employee.email,
            'current_utilization': round(total_allocation, 1),
            'available_capacity': round(available_capacity, 1),
            'project_id': project.id,
            'project_name': project.project_name,
            'client_name': project.client_name,
            'project_status': project.status.value if project.status else None,
            'required_skill': skill_name,
            'current_proficiency': current_prof,
            'required_proficiency': required_prof,
            'match_score': round(candidate['match_score'], 1),
            'training_recommendation': self._get_training_recommendation(skill_name, required_prof, current_prof),
            'training_cost': round(training_cost, 2),
            'hiring_cost': round(hiring_cost, 2),
            'cost_savings': round(cost_savings, 2),
            'time_savings_days': time_savings,
            'business_benefits': self._get_business_benefits(cost_savings, time_savings),
            'employee_benefits': self._get_employee_benefits(skill_name, project)
        }
    
    def _estimate_training_cost(self, skill: str, target_proficiency: int, current_proficiency: int) -> float:
        """Estimate training cost based on skill and proficiency gap"""
        # Base training costs (in USD, simplified)
        base_costs = {
            'Python': 500,
            'Java': 600,
            'JavaScript': 400,
            'React': 450,
            'AWS': 800,
            'Azure': 800,
            'Appian': 1000,
            'Docker': 300,
            'Kubernetes': 500,
            'Machine Learning': 1000
        }
        
        base_cost = base_costs.get(skill, 500)  # Default
        
        # Adjust based on proficiency gap
        proficiency_gap = target_proficiency - current_proficiency
        if proficiency_gap <= 1:
            multiplier = 0.5  # Quick upskill
        elif proficiency_gap == 2:
            multiplier = 1.0  # Standard training
        else:
            multiplier = 1.5  # Comprehensive training
        
        return base_cost * multiplier
    
    def _estimate_hiring_cost(self, role_level: str, skill: str) -> float:
        """Estimate cost of hiring a new employee with this skill"""
        # Base hiring costs (in USD, simplified - includes recruitment, onboarding, etc.)
        base_costs = {
            'JR': 5000,
            'MID': 8000,
            'SR': 12000,
            'LEAD': 15000,
            'PRINCIPAL': 20000
        }
        
        base_cost = base_costs.get(role_level, 10000)
        
        # Add skill premium
        premium_skills = ['Appian', 'AWS', 'Azure', 'Machine Learning', 'Kubernetes']
        if skill in premium_skills:
            base_cost *= 1.3
        
        return base_cost
    
    def _get_training_recommendation(self, skill: str, target_prof: int, current_prof: int) -> str:
        """Get specific training recommendation"""
        if current_prof == 0:
            return f"{skill} Fundamentals Course - Complete beginner to intermediate level training"
        elif current_prof < target_prof:
            gap = target_prof - current_prof
            if gap == 1:
                return f"{skill} Advanced Workshop - 1-week intensive training"
            else:
                return f"{skill} Comprehensive Certification Program - {gap}-week structured training"
        return f"{skill} Refresher Course"
    
    def _get_business_benefits(self, cost_savings: float, time_savings: int) -> List[str]:
        """Generate business benefits list"""
        benefits = [
            f"Save ${cost_savings:,.0f} compared to hiring a new employee",
            f"Reduce time-to-productivity by {time_savings} days",
            "Leverage existing employee knowledge and company context",
            "Improve employee retention through skill development",
            "Reduce recruitment and onboarding overhead"
        ]
        return benefits
    
    def _get_employee_benefits(self, skill: str, project: Project) -> List[str]:
        """Generate employee benefits list"""
        benefits = [
            f"Gain valuable {skill} skills for career growth",
            f"Increase future market value and billing potential",
            f"Better alignment with upcoming {project.project_name} project",
            "Enhanced skill portfolio for future project opportunities",
            "Professional development and career advancement"
        ]
        return benefits
    
    def _generate_ai_insights(self, recommendations: List[Dict]) -> Optional[str]:
        """Generate AI-powered insights using Gemini"""
        if not self.model or not recommendations:
            return None
        
        try:
            prompt = f"""
            Analyze these training recommendations and provide strategic insights:
            
            Total Recommendations: {len(recommendations)}
            Total Cost Savings: ${sum(r.get('cost_savings', 0) for r in recommendations):,.0f}
            
            Top Recommendations:
            {chr(10).join([f"- {r['employee_name']} → {r['required_skill']} for {r['project_name']} (Save ${r.get('cost_savings', 0):,.0f})" for r in recommendations[:5]])}
            
            Provide 2-3 strategic insights in simple, business-friendly language explaining:
            1. Why upskilling is preferred over hiring for these scenarios
            2. Key business advantages (cost, time, retention)
            3. Employee growth and value proposition
            
            Keep it concise and actionable.
            """
            
            response = self.model.generate_content(prompt)
            return response.text if response else None
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return None
