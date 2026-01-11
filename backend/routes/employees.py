"""
Employee Management Routes
CRUD operations for employees, 360 view, availability timeline
"""
from flask import Blueprint, request, jsonify
from models import Employee, EmployeeSkill, Allocation, Feedback360, BenchLedger, EmployeeStatus, RoleLevel
from tools.sql_db import SQLDatabaseTool
from datetime import datetime, date
from sqlalchemy import and_, or_

bp = Blueprint('employees', __name__)
db_tool = SQLDatabaseTool()

@bp.route('/', methods=['GET'])
def get_employees():
    """
    Get all employees with optional filtering
    Query params: status, role_level, search
    """
    session = db_tool.Session()
    try:
        query = session.query(Employee)

        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter(Employee.status == EmployeeStatus(status.upper()))

        role_level = request.args.get('role_level')
        if role_level:
            query = query.filter(Employee.role_level == RoleLevel(role_level.upper()))

        search = request.args.get('search')
        if search:
            query = query.filter(
                or_(
                    Employee.first_name.ilike(f'%{search}%'),
                    Employee.last_name.ilike(f'%{search}%'),
                    Employee.email.ilike(f'%{search}%')
                )
            )

        employees = query.all()

        result = []
        for emp in employees:
            result.append({
                'id': emp.id,
                'uuid': emp.uuid,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'role_level': emp.role_level.name if emp.role_level else None,
                'ctc_monthly': emp.ctc_monthly,
                'base_location': emp.base_location,
                'visa_status': emp.visa_status,
                'remote_pref': emp.remote_pref,
                'status': emp.status.value if emp.status else None,
                'joined_date': emp.joined_date.isoformat() if emp.joined_date else None,
                'bio_summary': emp.bio_summary,
                'skills_count': len(emp.skills),
                'allocations_count': len(emp.allocations)
            })

        return jsonify({
            'employees': result,
            'count': len(result)
        })
    finally:
        session.close()

@bp.route('/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    """
    Get detailed 360 view of an employee
    """
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Get current allocation
        current_allocation = session.query(Allocation).filter(
            and_(
                Allocation.emp_id == emp_id,
                Allocation.end_date.is_(None) | (Allocation.end_date >= date.today())
            )
        ).first()

        # Get skills
        skills = [{
            'id': skill.id,
            'skill_name': skill.skill_name,
            'proficiency': skill.proficiency,
            'last_used': skill.last_used.isoformat() if skill.last_used else None,
            'is_verified': skill.is_verified
        } for skill in employee.skills]

        # Get feedback history
        feedbacks = [{
            'id': fb.id,
            'project_name': fb.project.project_name if fb.project else 'Unknown',
            'rating': fb.rating,
            'feedback': fb.feedback,
            'tags': fb.tags
        } for fb in employee.feedbacks]

        # Get allocation history
        allocations = [{
            'id': alloc.id,
            'project_name': alloc.project.project_name if alloc.project else 'Unknown',
            'client_name': alloc.project.client_name if alloc.project else 'Unknown',
            'start_date': alloc.start_date.isoformat(),
            'end_date': alloc.end_date.isoformat() if alloc.end_date else None,
            'billing_rate': alloc.billing_rate,
            'utilization': alloc.utilization
        } for alloc in employee.allocations]

        # Get bench history
        bench_entries = [{
            'id': entry.id,
            'start_date': entry.start_date.isoformat(),
            'end_date': entry.end_date.isoformat() if entry.end_date else None,
            'reason': entry.reason,
            'cost_incurred': entry.cost_incurred
        } for entry in employee.bench_entries]

        # Calculate availability timeline
        availability = calculate_availability_timeline(employee, session)

        return jsonify({
            'employee': {
                'id': employee.id,
                'uuid': employee.uuid,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'role_level': employee.role_level.name if employee.role_level else None,
                'ctc_monthly': employee.ctc_monthly,
                'currency': employee.currency,
                'base_location': employee.base_location,
                'visa_status': employee.visa_status,
                'remote_pref': employee.remote_pref,
                'status': employee.status.value if employee.status else None,
                'joined_date': employee.joined_date.isoformat() if employee.joined_date else None,
                'bio_summary': employee.bio_summary
            },
            'current_allocation': {
                'project_name': current_allocation.project.project_name if current_allocation and current_allocation.project else None,
                'start_date': current_allocation.start_date.isoformat() if current_allocation else None,
                'billing_rate': current_allocation.billing_rate if current_allocation else None
            } if current_allocation else None,
            'skills': skills,
            'feedbacks': feedbacks,
            'allocations': allocations,
            'bench_history': bench_entries,
            'availability_timeline': availability
        })
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_employee():
    """
    Create a new employee
    """
    data = request.get_json()
    session = db_tool.Session()
    try:
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'role_level', 'ctc_monthly']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Check if email already exists
        existing = session.query(Employee).filter(Employee.email == data['email']).first()
        if existing:
            return jsonify({'error': 'Employee with this email already exists'}), 400

        # Create employee
        employee = Employee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            role_level=RoleLevel(data['role_level'].upper()),
            ctc_monthly=data['ctc_monthly'],
            currency=data.get('currency', 'USD'),
            base_location=data.get('base_location'),
            visa_status=data.get('visa_status'),
            remote_pref=data.get('remote_pref', False),
            status=EmployeeStatus(data.get('status', 'BENCH').upper()),
            joined_date=datetime.strptime(data['joined_date'], '%Y-%m-%d').date() if data.get('joined_date') else date.today(),
            bio_summary=data.get('bio_summary')
        )

        session.add(employee)
        session.commit()
        session.refresh(employee)

        # Add skills if provided
        if data.get('skills'):
            for skill_data in data['skills']:
                skill = EmployeeSkill(
                    emp_id=employee.id,
                    skill_name=skill_data['skill_name'],
                    proficiency=skill_data['proficiency'],
                    last_used=datetime.strptime(skill_data['last_used'], '%Y-%m-%d').date() if skill_data.get('last_used') else None,
                    is_verified=skill_data.get('is_verified', False)
                )
                session.add(skill)
            session.commit()

        return jsonify({
            'success': True,
            'message': 'Employee created successfully',
            'employee_id': employee.id,
            'uuid': employee.uuid
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """
    Update employee information
    """
    data = request.get_json()
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Update fields
        updatable_fields = [
            'first_name', 'last_name', 'email', 'role_level', 'ctc_monthly',
            'currency', 'base_location', 'visa_status', 'remote_pref',
            'status', 'bio_summary'
        ]

        for field in updatable_fields:
            if field in data:
                if field == 'role_level':
                    setattr(employee, field, RoleLevel(data[field].upper()))
                elif field == 'status':
                    setattr(employee, field, EmployeeStatus(data[field].upper()))
                else:
                    setattr(employee, field, data[field])

        if 'joined_date' in data:
            employee.joined_date = datetime.strptime(data['joined_date'], '%Y-%m-%d').date()

        session.commit()

        return jsonify({
            'success': True,
            'message': 'Employee updated successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """
    Delete an employee (soft delete by setting status)
    """
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Instead of hard delete, mark as inactive or remove from bench
        # For now, we'll change status to indicate removal
        employee.status = EmployeeStatus.BENCH  # Or create a TERMINATED status

        session.commit()

        return jsonify({
            'success': True,
            'message': 'Employee removed successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:emp_id>/availability', methods=['GET'])
def get_employee_availability(emp_id):
    """
    Get detailed availability timeline for an employee
    """
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        availability = calculate_availability_timeline(employee, session)

        return jsonify({
            'employee_id': emp_id,
            'availability_timeline': availability
        })
    finally:
        session.close()

def calculate_availability_timeline(employee, session):
    """
    Calculate availability timeline based on allocations and bench periods
    """
    # Get all allocations and bench entries
    allocations = session.query(Allocation).filter(Allocation.emp_id == employee.id).all()
    bench_entries = session.query(BenchLedger).filter(BenchLedger.emp_id == employee.id).all()

    timeline = []

    # Add allocation periods
    for alloc in allocations:
        timeline.append({
            'type': 'allocated',
            'start_date': alloc.start_date.isoformat(),
            'end_date': alloc.end_date.isoformat() if alloc.end_date else None,
            'project_name': alloc.project.project_name if alloc.project else 'Unknown',
            'client_name': alloc.project.client_name if alloc.project else 'Unknown',
            'billing_rate': alloc.billing_rate,
            'utilization': alloc.utilization
        })

    # Add bench periods
    for bench in bench_entries:
        timeline.append({
            'type': 'bench',
            'start_date': bench.start_date.isoformat(),
            'end_date': bench.end_date.isoformat() if bench.end_date else None,
            'reason': bench.reason,
            'cost_incurred': bench.cost_incurred
        })

    # Sort by start date
    timeline.sort(key=lambda x: x['start_date'])

    return timeline

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
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(
            Employee.uuid == emp_uuid
        ).first()

        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Find project
        from models import Project
        project = session.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Validate allocation (simplified auditor logic)
        if employee.status != EmployeeStatus.BENCH:
            return jsonify({'error': f'Employee is not on bench (current status: {employee.status.value})'}), 400

        # Check if employee CTC fits within project budget (if budget_cap is set)
        if project.budget_cap and employee.ctc_monthly > project.budget_cap:
            return jsonify({'error': f'Employee CTC ({employee.ctc_monthly}) exceeds project budget cap ({project.budget_cap})'}), 400

        # Create allocation
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        allocation = Allocation(
            emp_id=employee.id,
            proj_id=project_id,
            start_date=start_date,
            end_date=end_date,
            billing_rate=billing_rate,
            is_revealed=True  # Reveal immediately upon allocation
        )

        session.add(allocation)

        # Update employee status to allocated
        employee.status = EmployeeStatus.ALLOCATED
        session.commit()

        # Return success with unmasked employee profile
        return jsonify({
            'message': 'Resource allocated successfully',
            'employee': {
                'id': employee.id,
                'uuid': employee.uuid,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'role_level': employee.role_level.value if employee.role_level else None,
                'base_location': employee.base_location,
                'ctc_monthly': employee.ctc_monthly,
                'status': employee.status.value if employee.status else None
            },
            'allocation': {
                'project_id': project_id,
                'project_name': project.project_name,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat() if end_date else None,
                'billing_rate': billing_rate
            }
        })

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()