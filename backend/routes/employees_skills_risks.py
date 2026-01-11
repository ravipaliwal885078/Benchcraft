"""
Additional Employee Routes for Skills and Risk Management
"""
from flask import Blueprint, request, jsonify
from models import Employee, EmployeeSkill, RiskRegister, RiskType, RiskSeverity, RiskStatus, Project
from tools.sql_db import SQLDatabaseTool
from datetime import datetime, date
from sqlalchemy import and_

bp = Blueprint('employee_skills_risks', __name__)
db_tool = SQLDatabaseTool()


@bp.route('/<int:emp_id>/skills', methods=['POST'])
def add_employee_skill(emp_id):
    """
    Add a skill to an employee
    Input: { skill_name, proficiency (1-5), last_used (optional), is_verified (optional) }
    """
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        skill_name = data.get('skill_name')
        proficiency_raw = data.get('proficiency', 3)
        
        if not skill_name:
            return jsonify({'error': 'skill_name is required'}), 400
        
        # Convert proficiency to integer
        try:
            proficiency = int(proficiency_raw)
        except (ValueError, TypeError):
            return jsonify({'error': 'proficiency must be a number between 1 and 5'}), 400
        
        if proficiency < 1 or proficiency > 5:
            return jsonify({'error': 'proficiency must be between 1 and 5'}), 400
        
        # Check if skill already exists
        existing_skill = session.query(EmployeeSkill).filter(
            and_(
                EmployeeSkill.emp_id == emp_id,
                EmployeeSkill.skill_name == skill_name
            )
        ).first()
        
        if existing_skill:
            # Update existing skill
            existing_skill.proficiency = proficiency
            existing_skill.last_used = datetime.strptime(data['last_used'], '%Y-%m-%d').date() if data.get('last_used') else None
            existing_skill.is_verified = data.get('is_verified', False)
        else:
            # Create new skill
            skill = EmployeeSkill(
                emp_id=emp_id,
                skill_name=skill_name,
                proficiency=proficiency,
                last_used=datetime.strptime(data['last_used'], '%Y-%m-%d').date() if data.get('last_used') else None,
                is_verified=data.get('is_verified', False)
            )
            session.add(skill)
        
        session.commit()
        return jsonify({'message': 'Skill added successfully'}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/<int:emp_id>/skills/<int:skill_id>', methods=['DELETE'])
def remove_employee_skill(emp_id, skill_id):
    """
    Remove a skill from an employee
    """
    session = db_tool.Session()
    try:
        skill = session.query(EmployeeSkill).filter(
            and_(
                EmployeeSkill.id == skill_id,
                EmployeeSkill.emp_id == emp_id
            )
        ).first()
        
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        session.delete(skill)
        session.commit()
        return jsonify({'message': 'Skill removed successfully'}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/<int:emp_id>/risks', methods=['POST'])
def raise_employee_risk(emp_id):
    """
    Raise a risk for an employee
    Input: { 
        project_id (optional), 
        risk_type, 
        severity, 
        description, 
        mitigation_plan (optional),
        mitigation_owner_emp_id (optional),
        target_resolution_date (optional)
    }
    """
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        risk_type_str = data.get('risk_type')
        severity_str = data.get('severity')
        description = data.get('description')
        
        if not all([risk_type_str, severity_str, description]):
            return jsonify({'error': 'risk_type, severity, and description are required'}), 400
        
        # Validate enums
        try:
            risk_type = RiskType[risk_type_str.upper()]
            severity = RiskSeverity[severity_str.upper()]
        except KeyError as e:
            return jsonify({'error': f'Invalid enum value: {str(e)}'}), 400
        
        # Validate project if provided
        project_id = data.get('project_id')
        if project_id:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return jsonify({'error': 'Project not found'}), 404
        
        # Validate mitigation owner if provided
        mitigation_owner_emp_id = data.get('mitigation_owner_emp_id')
        if mitigation_owner_emp_id:
            owner = session.query(Employee).filter(Employee.id == mitigation_owner_emp_id).first()
            if not owner:
                return jsonify({'error': 'Mitigation owner not found'}), 404
        
        # Create risk
        risk = RiskRegister(
            emp_id=emp_id,
            project_id=project_id,
            risk_type=risk_type,
            severity=severity,
            description=description,
            mitigation_plan=data.get('mitigation_plan'),
            mitigation_owner_emp_id=mitigation_owner_emp_id,
            identified_date=date.today(),
            target_resolution_date=datetime.strptime(data['target_resolution_date'], '%Y-%m-%d').date() if data.get('target_resolution_date') else None,
            status=RiskStatus.OPEN
        )
        
        session.add(risk)
        session.commit()
        session.refresh(risk)
        
        return jsonify({
            'message': 'Risk raised successfully',
            'risk': {
                'id': risk.id,
                'emp_id': risk.emp_id,
                'project_id': risk.project_id,
                'risk_type': risk.risk_type.value,
                'severity': risk.severity.value,
                'status': risk.status.value
            }
        }), 201
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
