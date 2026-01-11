"""
Team Suggestion Agent - AI-powered team allocation recommendations
Considers availability, skills, experience, domains, and allocation constraints
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
from models import Employee, Allocation, EmployeeSkill, EmployeeDomain, ProjectDomain, Domain, Project
from datetime import date, datetime
from typing import List, Dict, Optional
from sqlalchemy import and_, or_, func
import google.generativeai as genai
import os

class TeamSuggestionAgent(BaseAgent):
    """AI Agent for suggesting optimal team allocations"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        self.llm = None
        self._init_llm()
        super().__init__(
            role="Team Allocation Strategist",
            goal="Suggest optimal team members for projects based on availability, skills, experience, and allocation constraints",
            backstory="You are an expert resource manager who analyzes employee profiles, availability, skills, and project requirements to suggest the best team composition."
        )
    
    def _init_llm(self):
        """Initialize Gemini LLM with lazy loading"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                # Try different model names
                model_names = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
                for model_name in model_names:
                    try:
                        self.llm = genai.GenerativeModel(model_name)
                        # Test the model
                        self.llm.generate_content("test")
                        print(f"TeamSuggestionAgent: Using model {model_name}")
                        break
                    except Exception:
                        continue
        except Exception as e:
            print(f"TeamSuggestionAgent: LLM initialization failed: {e}")
            self.llm = None
    
    def suggest_team(
        self,
        project_id: Optional[int],
        project_details: Dict,
        role_requirements: List[Dict],
        start_date: str,
        end_date: Optional[str]
    ) -> Dict:
        """
        Suggest team members for each role requirement
        
        Args:
            project_id: Optional project ID (for existing projects)
            project_details: Project information (description, tech_stack, industry_domain, etc.)
            role_requirements: List of {role_name, required_count, utilization_percentage}
            start_date: Project start date (YYYY-MM-DD)
            end_date: Project end date (YYYY-MM-DD) or None
        
        Returns:
            {
                'suggestions': [
                    {
                        'role_name': str,
                        'employee_id': int,
                        'allocation_percentage': int,
                        'billable_percentage': int,
                        'billing_rate': float,
                        'match_score': float,
                        'match_reasons': List[str]
                    }
                ],
                'insights': str,  # AI-generated insights
                'benefits': str    # AI-generated benefits
            }
        """
        session = self.db_tool.Session()
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Get all available employees
            all_employees = session.query(Employee).all()
            
            suggestions = []
            employee_allocation_map = {}  # Track total allocation per employee
            
            # For each role requirement
            for role_req in role_requirements:
                role_name = role_req['role_name']
                required_count = role_req['required_count']
                utilization_pct = role_req['utilization_percentage']
                
                # Find candidates for this role
                candidates = self._find_candidates(
                    session,
                    role_name,
                    project_details,
                    start_date_obj,
                    end_date_obj,
                    employee_allocation_map,
                    utilization_pct
                )
                
                # Select top candidates
                selected = candidates[:required_count]
                
                for candidate in selected:
                    emp_id = candidate['employee_id']
                    allocation_pct = candidate['suggested_allocation']
                    
                    # Update allocation map
                    if emp_id not in employee_allocation_map:
                        employee_allocation_map[emp_id] = 0
                    employee_allocation_map[emp_id] += allocation_pct
                    
                    # Get billing rate
                    billing_rate = self._get_billing_rate(session, emp_id, project_details.get('industry_domain'))
                    
                    suggestions.append({
                        'role_name': role_name,
                        'employee_id': emp_id,
                        'allocation_percentage': allocation_pct,
                        'billable_percentage': 100,  # Default to 100% billable
                        'billing_rate': billing_rate,
                        'match_score': candidate['match_score'],
                        'match_reasons': candidate['reasons']
                    })
            
            # Generate AI insights
            insights_data = {
                'project': project_details,
                'role_requirements': role_requirements,
                'suggestions': suggestions
            }
            insights = self._generate_insights(insights_data, session)
            benefits = self._generate_benefits(insights_data, session)
            
            return {
                'suggestions': suggestions,
                'insights': insights,
                'benefits': benefits
            }
            
        finally:
            session.close()
    
    def _find_candidates(
        self,
        session,
        role_name: str,
        project_details: Dict,
        start_date: date,
        end_date: Optional[date],
        employee_allocation_map: Dict[int, float],
        required_utilization: int
    ) -> List[Dict]:
        """Find and rank candidates for a role"""
        all_employees = session.query(Employee).all()
        candidates = []
        
        # Extract project requirements
        tech_stack = project_details.get('tech_stack', '')
        if isinstance(tech_stack, list):
            tech_stack = ', '.join(tech_stack)
        industry_domain = project_details.get('industry_domain', '')
        description = project_details.get('description', '')
        
        for emp in all_employees:
            # Check availability
            availability = self._check_availability(
                session,
                emp.id,
                start_date,
                end_date,
                employee_allocation_map.get(emp.id, 0),
                required_utilization
            )
            
            if not availability['available']:
                continue
            
            # Calculate match score
            match_score, reasons = self._calculate_match_score(
                session,
                emp,
                role_name,
                tech_stack,
                industry_domain,
                description,
                availability
            )
            
            candidates.append({
                'employee_id': emp.id,
                'employee': emp,
                'match_score': match_score,
                'reasons': reasons,
                'suggested_allocation': availability['suggested_allocation'],
                'availability': availability
            })
        
        # Sort by match score (descending)
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        return candidates
    
    def _check_availability(
        self,
        session,
        emp_id: int,
        start_date: date,
        end_date: Optional[date],
        current_allocation: float,
        required_utilization: int
    ) -> Dict:
        """Check if employee is available for the date range"""
        # Get existing allocations that overlap
        query = session.query(Allocation).filter(
            Allocation.emp_id == emp_id,
            or_(
                Allocation.end_date.is_(None),
                Allocation.end_date >= start_date
            )
        )
        
        if end_date:
            query = query.filter(
                or_(
                    Allocation.start_date.is_(None),
                    Allocation.start_date <= end_date
                )
            )
        
        overlapping_allocations = query.all()
        
        # Calculate total allocation in the date range
        total_allocation = current_allocation
        for alloc in overlapping_allocations:
            if alloc.allocation_percentage:
                total_allocation += alloc.allocation_percentage
        
        # Check if we can add this allocation
        suggested_allocation = min(required_utilization, 100 - total_allocation)
        
        if suggested_allocation <= 0:
            return {
                'available': False,
                'reason': f'Already allocated {total_allocation}%',
                'suggested_allocation': 0
            }
        
        return {
            'available': True,
            'current_total': total_allocation,
            'suggested_allocation': suggested_allocation,
            'reason': f'Available: {100 - total_allocation}% free'
        }
    
    def _calculate_match_score(
        self,
        session,
        employee: Employee,
        role_name: str,
        tech_stack: str,
        industry_domain: str,
        description: str,
        availability: Dict
    ) -> tuple:
        """Calculate match score and reasons"""
        score = 0.0
        reasons = []
        
        # Role level matching (basic heuristic)
        role_level_map = {
            'Architect': ['PRINCIPAL', 'LEAD'],
            'Project Manager': ['LEAD', 'SR'],
            'Senior Developer': ['SR', 'LEAD'],
            'Developer': ['MID', 'SR', 'JR'],
            'Business Analyst': ['MID', 'SR'],
            'QA Engineer': ['MID', 'SR'],
            'Tech Lead': ['LEAD', 'SR'],
            'Designer': ['MID', 'SR']
        }
        
        expected_levels = role_level_map.get(role_name, [])
        # employee.role_level is stored as string, not enum
        employee_role_level = employee.role_level if isinstance(employee.role_level, str) else (employee.role_level.value if hasattr(employee.role_level, 'value') else str(employee.role_level))
        if employee_role_level in expected_levels:
            score += 30
            reasons.append(f"Role level ({employee_role_level}) matches {role_name}")
        else:
            reasons.append(f"Role level ({employee_role_level}) may not be ideal for {role_name}")
        
        # Skills matching
        tech_list = [t.strip() for t in tech_stack.split(',')] if tech_stack else []
        employee_skills = {skill.skill_name.lower(): skill.proficiency for skill in employee.skills}
        
        matching_skills = []
        skill_score = 0
        for tech in tech_list:
            tech_lower = tech.lower()
            for skill_name, proficiency in employee_skills.items():
                if tech_lower in skill_name or skill_name in tech_lower:
                    matching_skills.append(f"{skill_name} (proficiency: {proficiency})")
                    skill_score += proficiency * 5
                    break
        
        if matching_skills:
            score += min(skill_score, 40)
            reasons.append(f"Has relevant skills: {', '.join(matching_skills[:3])}")
        else:
            reasons.append("Limited matching skills for tech stack")
        
        # Domain experience
        if industry_domain:
            emp_domains = session.query(EmployeeDomain).join(Domain).filter(
                EmployeeDomain.emp_id == employee.id
            ).all()
            
            domain_match = False
            for emp_domain in emp_domains:
                if industry_domain.lower() in emp_domain.domain.domain_name.lower():
                    score += 20
                    reasons.append(f"Has experience in {industry_domain} domain")
                    domain_match = True
                    break
            
            if not domain_match:
                reasons.append(f"No direct experience in {industry_domain} domain")
        
        # Availability bonus
        if availability['available']:
            free_percentage = 100 - availability['current_total']
            if free_percentage >= required_utilization:
                score += 10
                reasons.append("Fully available for required allocation")
            else:
                reasons.append(f"Partially available ({free_percentage}% free)")
        
        # Status bonus (bench employees get slight boost)
        employee_status = employee.status.value if hasattr(employee.status, 'value') else str(employee.status)
        if employee_status == 'BENCH':
            score += 5
            reasons.append("Currently on bench - ready to allocate")
        
        return round(score, 2), reasons
    
    def _get_billing_rate(self, session, emp_id: int, industry_domain: Optional[str]) -> Optional[float]:
        """Get appropriate billing rate for employee"""
        from models import RateCard, RateType
        
        # Try domain-specific rate first
        if industry_domain:
            domain = session.query(Domain).filter(
                Domain.domain_name.ilike(f'%{industry_domain}%')
            ).first()
            
            if domain:
                domain_rate = session.query(RateCard).filter(
                    RateCard.emp_id == emp_id,
                    RateCard.domain_id == domain.id,
                    RateCard.is_active == True
                ).order_by(RateCard.effective_date.desc()).first()
                
                if domain_rate:
                    return round(domain_rate.hourly_rate, 2)
        
        # Fall back to base rate
        base_rate = session.query(RateCard).filter(
            RateCard.emp_id == emp_id,
            RateCard.rate_type == RateType.BASE,
            RateCard.is_active == True
        ).order_by(RateCard.effective_date.desc()).first()
        
        if base_rate:
            return round(base_rate.hourly_rate, 2)
        
        return None
    
    def _generate_insights(self, data: Dict, session) -> str:
        """Generate AI insights about team suggestions"""
        if not self.llm:
            return self._rule_based_insights(data, session)
        
        try:
            project = data['project']
            role_reqs = data['role_requirements']
            suggestions = data['suggestions']
            
            # Build context
            context = f"""
Project: {project.get('project_name', 'New Project')}
Industry: {project.get('industry_domain', 'N/A')}
Tech Stack: {project.get('tech_stack', 'N/A')}
Description: {project.get('description', '')[:500]}

Role Requirements:
"""
            for req in role_reqs:
                context += f"- {req['role_name']}: {req['required_count']} required, {req['utilization_percentage']}% utilization\n"
            
            context += "\nSuggested Team:\n"
            for sug in suggestions:
                emp = session.query(Employee).filter(Employee.id == sug['employee_id']).first()
                if emp:
                    context += f"- {emp.first_name} {emp.last_name} ({sug['role_name']}): {sug['match_score']}/100 match score\n"
                    context += f"  Reasons: {', '.join(sug['match_reasons'][:2])}\n"
            
            prompt = f"""
Based on the following project and team suggestions, provide a brief (2-3 sentences) insight explaining why these specific employees were suggested for their roles. Focus on:
- Skill alignment with project requirements
- Domain experience relevance
- Availability and allocation optimization
- Team composition strengths

{context}

Provide only the insight explanation, no markdown formatting.
"""
            
            response = self.llm.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return self._rule_based_insights(data, session)
    
    def _generate_benefits(self, data: Dict, session) -> str:
        """Generate AI benefits explanation"""
        if not self.llm:
            return self._rule_based_benefits(data, session)
        
        try:
            project = data['project']
            suggestions = data['suggestions']
            
            context = f"""
Project: {project.get('project_name', 'New Project')}
Industry: {project.get('industry_domain', 'N/A')}

Suggested Team Composition:
"""
            for sug in suggestions:
                emp = session.query(Employee).filter(Employee.id == sug['employee_id']).first()
                if emp:
                    context += f"- {emp.first_name} {emp.last_name} as {sug['role_name']}\n"
            
            prompt = f"""
Based on the suggested team composition, provide a brief (2-3 sentences) explanation of the benefits of this team setup. Focus on:
- How this team composition benefits the project
- Resource optimization advantages
- Skill coverage and expertise
- Risk mitigation

{context}

Provide only the benefits explanation, no markdown formatting.
"""
            
            response = self.llm.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Error generating AI benefits: {e}")
            return self._rule_based_benefits(data, session)
    
    def _rule_based_insights(self, data: Dict, session) -> str:
        """Fallback rule-based insights"""
        insights = []
        suggestions = data['suggestions']
        
        # Count by role level
        role_levels = {}
        for sug in suggestions:
            emp = session.query(Employee).filter(Employee.id == sug['employee_id']).first()
            if emp:
                level = emp.role_level
                role_levels[level] = role_levels.get(level, 0) + 1
        
        if role_levels:
            insights.append(f"Team composition includes {', '.join([f'{count} {level}' for level, count in role_levels.items()])}.")
        
        # Skill coverage
        tech_stack = data['project'].get('tech_stack', '')
        if tech_stack:
            insights.append("Selected team members have relevant skills matching the project's tech stack requirements.")
        
        return " ".join(insights) if insights else "Team suggestions based on availability, skills, and experience matching."
    
    def _rule_based_benefits(self, data: Dict, session) -> str:
        """Fallback rule-based benefits"""
        benefits = []
        
        # Availability
        total_allocation = sum([s.get('allocation_percentage', 0) for s in data['suggestions']])
        if total_allocation > 0:
            benefits.append("Optimized allocation ensures efficient resource utilization.")
        
        # Domain experience
        industry = data['project'].get('industry_domain', '')
        if industry:
            benefits.append(f"Team members with {industry} domain experience bring relevant expertise.")
        
        benefits.append("Balanced team composition supports project delivery success.")
        
        return " ".join(benefits)
