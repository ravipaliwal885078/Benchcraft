"""
Resource Management Routes
/search - Blind talent search
/allocate - Resource allocation
"""
from flask import Blueprint, request, jsonify
from agents.scout import ScoutAgent
from agents.matchmaker import MatchmakerAgent
from agents.auditor import AuditorAgent
from tools.sql_db import SQLDatabaseTool
from datetime import datetime

bp = Blueprint('resources', __name__)
scout = ScoutAgent()
matchmaker = MatchmakerAgent()
auditor = AuditorAgent()
db_tool = SQLDatabaseTool()

@bp.route('/search', methods=['POST'])
def search_talent():
    data = request.get_json()
    query = data.get('query', '')
    min_proficiency = data.get('min_proficiency', 1)
    max_budget = data.get('max_budget')
    
    # Extract the new advanced filters
    role_level = data.get('roleLevel')
    location = data.get('location')
    remote_only = data.get('remoteOnly')
    visa_required = data.get('visaRequired')
    project_type = data.get('projectType')

    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Step 1: Scout finds matches based on query and proficiency
    search_results = scout.search(query, min_proficiency)
    
    # Step 2: Apply advanced filtering
    filtered_results = []
    for result in search_results:
        emp = db_tool.get_employee(result['emp_id'])
        if not emp:
            continue
            
        # Check Budget
        if max_budget and emp.ctc_monthly > float(max_budget):
            continue
            
        # Check Role Level
        if role_level and emp.role_level.value != role_level:
            continue
            
        # Check Location
        if location and location.lower() not in emp.base_location.lower():
            continue

        # If all checks pass, add to results
        filtered_results.append(result)
        
    search_results = filtered_results
    
    # Step 3: Matchmaker anonymizes results
    emp_ids = [r['emp_id'] for r in search_results]
    match_scores = {r['emp_id']: r['match_score'] for r in search_results}
    anonymized_profiles = matchmaker.anonymize_search_results(emp_ids, match_scores)
    
    return jsonify({
        'results': anonymized_profiles,
        'count': len(anonymized_profiles)
    })
@bp.route('/allocate', methods=['POST'])
def allocate_resource():
    """
    Allocate resource to project
    Input: { emp_uuid, project_id, start_date, end_date, billing_rate }
    Output: Success message + unmasked employee profile
    """
    data = request.get_json()
    emp_uuid = data.get('emp_uuid')
    project_id = data.get('project_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    billing_rate = data.get('billing_rate')
    
    if not all([emp_uuid, project_id, start_date_str]):
        return jsonify({'error': 'emp_uuid, project_id, and start_date are required'}), 400
    
    # Find employee by UUID
    from models import Employee
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(
            Employee.uuid == emp_uuid
        ).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Step 1: Auditor validates
        is_valid, reason = auditor.validate_allocation(employee.id, project_id)
        if not is_valid:
            return jsonify({'error': reason}), 400
        
        # Step 2: Create allocation
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        # Validate allocation percentage (default to 100% if not provided)
        allocation_percentage = data.get('allocation_percentage', 100)
        internal_allocation_percentage = data.get('internal_allocation_percentage', allocation_percentage)  # Default to allocation_percentage if not provided
        billable_percentage = data.get('billable_percentage', 100)
        
        # Validate total internal allocation doesn't exceed 100%
        from utils.allocation_validator import validate_allocation_percentage
        is_valid, error_msg = validate_allocation_percentage(
            session,
            employee.id,
            internal_allocation_percentage,  # Use internal_allocation_percentage for validation
            start_date,
            end_date
        )
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        from models import Allocation
        allocation = Allocation(
            emp_id=employee.id,
            proj_id=project_id,
            start_date=start_date,
            end_date=end_date,
            billing_rate=billing_rate,
            allocation_percentage=allocation_percentage,
            internal_allocation_percentage=internal_allocation_percentage,
            billable_percentage=billable_percentage,
            is_revealed=True  # Reveal immediately upon allocation
        )
        session.add(allocation)
        
        # Sync employee status based on actual allocations
        from utils.employee_status import sync_employee_status
        sync_employee_status(employee, session)
        
        session.commit()
        session.refresh(allocation)
        
        # Return unmasked profile
        employee_profile = {
            'id': employee.id,
            'uuid': employee.uuid,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'role_level': employee.role_level.value if employee.role_level else None,
            'ctc_monthly': employee.ctc_monthly,
            'base_location': employee.base_location,
            'bio_summary': employee.bio_summary,
            'skills': [
                {
                    'skill_name': skill.skill_name,
                    'proficiency': skill.proficiency
                }
                for skill in employee.skills
            ]
        }
        
        return jsonify({
            'success': True,
            'message': 'Resource allocated successfully',
            'allocation_id': allocation.id,
            'employee': employee_profile
        })
    finally:
        session.close()
