"""
Employee Management Routes
CRUD operations for employees, 360 view, availability timeline
"""
from flask import Blueprint, request, jsonify
from models import Employee, EmployeeSkill, Allocation, Feedback360, BenchLedger, EmployeeStatus, RoleLevel
from tools.sql_db import SQLDatabaseTool
from datetime import datetime, date
from sqlalchemy import and_, or_
from utils.allocation_validator import validate_allocation_percentage

bp = Blueprint('employees', __name__)
db_tool = SQLDatabaseTool()


def parse_role_level(role_level_str):
    """
    Safely parse role_level string to RoleLevel enum.
    Returns RoleLevel enum member or raises ValueError with helpful message.
    
    This function handles both member name access (RoleLevel["JR"]) and
    value access (RoleLevel("JR")) to ensure compatibility with SQLAlchemy.
    """
    if not role_level_str:
        raise ValueError("role_level is required")
    
    # Convert to string, uppercase, and strip whitespace
    role_level_str = str(role_level_str).upper().strip()
    
    # List of valid role level names and values
    valid_names = [member.name for member in RoleLevel]
    valid_values = [member.value for member in RoleLevel]
    
    # Try to access by member name first (preferred)
    if role_level_str in valid_names:
        try:
            return RoleLevel[role_level_str]
        except KeyError:
            pass
    
    # Fall back to value access (for SQLAlchemy compatibility)
    if role_level_str in valid_values:
        try:
            return RoleLevel(role_level_str)
        except ValueError:
            pass
    
    # If neither works, raise error with helpful message
    valid_options = ', '.join(valid_names)
    raise ValueError(
        f"'{role_level_str}' is not a valid RoleLevel. "
        f"Valid values are: {valid_options}"
    )

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
            try:
                role_level_enum = parse_role_level(role_level)
                query = query.filter(Employee.role_level == role_level_enum.value)  # Compare with string value
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

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
        today = date.today()

        result = []
        for emp in employees:
            # Get current allocation
            current_allocation = None
            try:
                current_allocation = session.query(Allocation).filter(
                    and_(
                        Allocation.emp_id == emp.id,
                        Allocation.start_date <= today,
                        or_(
                            Allocation.end_date.is_(None),
                            Allocation.end_date >= today
                        )
                    )
                ).first()
            except Exception:
                pass
            
            # Get current rate card
            current_rate_card = None
            hourly_rate = None
            try:
                from models import RateCard, RateType
                # Try to get base rate card
                base_rate = session.query(RateCard).filter(
                    and_(
                        RateCard.emp_id == emp.id,
                        RateCard.domain_id.is_(None),
                        RateCard.rate_type == RateType.BASE,
                        RateCard.is_active == True,
                        or_(
                            RateCard.expiry_date.is_(None),
                            RateCard.expiry_date >= today
                        )
                    )
                ).order_by(RateCard.effective_date.desc()).first()
                
                if base_rate:
                    current_rate_card = base_rate
                    hourly_rate = base_rate.hourly_rate
            except Exception:
                # RateCard table doesn't exist yet
                pass
            
            # Get skills
            skills = [{
                'id': skill.id,
                'skill_name': skill.skill_name,
                'proficiency': skill.proficiency,
                'is_verified': skill.is_verified
            } for skill in emp.skills]
            
            # Build employee data
            emp_data = {
                'id': emp.id,
                'uuid': emp.uuid,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'role_level': emp.role_level if emp.role_level else None,  # Already a string from DB
                'ctc_monthly': emp.ctc_monthly,
                'currency': emp.currency,
                'base_location': emp.base_location,
                'visa_status': emp.visa_status,
                'remote_pref': emp.remote_pref,
                'status': emp.status.value if emp.status else None,
                'joined_date': emp.joined_date.isoformat() if emp.joined_date else None,
                'bio_summary': emp.bio_summary,
                'skills': skills,
                'skills_count': len(skills),
                'allocations_count': len(emp.allocations),
                'current_allocation': None,
                'current_hourly_rate': hourly_rate
            }
            
            # Add current allocation details if exists
            if current_allocation:
                emp_data['current_allocation'] = {
                    'id': current_allocation.id,
                    'project_id': current_allocation.proj_id,
                    'project_name': current_allocation.project.project_name if current_allocation.project else None,
                    'client_name': current_allocation.project.client_name if current_allocation.project else None,
                    'start_date': current_allocation.start_date.isoformat() if current_allocation.start_date else None,
                    'end_date': current_allocation.end_date.isoformat() if current_allocation.end_date else None,
                    'billing_rate': current_allocation.billing_rate,
                    'allocation_percentage': current_allocation.allocation_percentage if hasattr(current_allocation, 'allocation_percentage') else (current_allocation.utilization if current_allocation.utilization else 100),
                    'billable_percentage': current_allocation.billable_percentage if hasattr(current_allocation, 'billable_percentage') else 100,
                    'utilization': current_allocation.allocation_percentage if hasattr(current_allocation, 'allocation_percentage') else (current_allocation.utilization if current_allocation.utilization else 100)  # Backward compatibility
                }
                # Use allocation billing rate if no rate card
                if not hourly_rate and current_allocation.billing_rate:
                    emp_data['current_hourly_rate'] = current_allocation.billing_rate
            
            result.append(emp_data)

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
            'project_id': fb.proj_id,
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
            'allocation_percentage': alloc.allocation_percentage if hasattr(alloc, 'allocation_percentage') else (alloc.utilization if alloc.utilization else 100),
            'billable_percentage': alloc.billable_percentage if hasattr(alloc, 'billable_percentage') else 100,
            'utilization': alloc.allocation_percentage if hasattr(alloc, 'allocation_percentage') else (alloc.utilization if alloc.utilization else 100)  # Backward compatibility
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
                'role_level': employee.role_level if employee.role_level else None,  # Already a string from DB
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

        # Validate and parse role_level
        role_level_input = data.get('role_level')
        print(f"DEBUG create_employee: Received role_level input: '{role_level_input}', type: {type(role_level_input)}")
        try:
            role_level_enum = parse_role_level(role_level_input)
            # Debug: Verify the enum is correct
            print(f"DEBUG: Parsed role_level: {role_level_enum}, type: {type(role_level_enum)}, name: {role_level_enum.name}, value: {role_level_enum.value}")
        except (ValueError, KeyError) as e:
            print(f"DEBUG create_employee: Error parsing role_level: {e}")
            return jsonify({'error': str(e)}), 400

        # Parse joined_date safely
        joined_date_value = date.today()
        if data.get('joined_date'):
            try:
                joined_date_value = datetime.strptime(data['joined_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError) as date_error:
                print(f"WARNING: Invalid joined_date format '{data.get('joined_date')}', using today's date. Error: {date_error}")
                joined_date_value = date.today()
        
        # Create employee - store enum value as string
        # Ensure role_level is a plain string, not an enum object
        role_level_str = str(role_level_enum.value)
        print(f"DEBUG: role_level_str before Employee creation: '{role_level_str}', type: {type(role_level_str)}")
        
        try:
            employee = Employee(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                role_level=role_level_str,  # Store as plain string
                ctc_monthly=float(data['ctc_monthly']),
                currency=data.get('currency', 'USD'),
                base_location=data.get('base_location'),
                visa_status=data.get('visa_status'),
                remote_pref=bool(data.get('remote_pref', False)),
                status=EmployeeStatus(data.get('status', 'BENCH').upper()),
                joined_date=joined_date_value,
                bio_summary=data.get('bio_summary')
            )
            print(f"DEBUG: Employee object created with role_level: '{employee.role_level}', type: {type(employee.role_level)}")
        except Exception as create_error:
            import traceback
            print(f"DEBUG: Error creating Employee object: {create_error}")
            print(traceback.format_exc())
            raise

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
    except ValueError as e:
        session.rollback()
        error_msg = str(e)
        if 'RoleLevel' in error_msg or 'not a valid' in error_msg.lower():
            return jsonify({
                'error': f'Invalid role_level. Valid values are: JR, MID, SR, LEAD, PRINCIPAL',
                'details': error_msg
            }), 400
        return jsonify({'error': error_msg}), 400
    except KeyError as e:
        session.rollback()
        error_msg = str(e)
        if 'RoleLevel' in error_msg:
            return jsonify({
                'error': f'Invalid role_level. Valid values are: JR, MID, SR, LEAD, PRINCIPAL',
                'details': error_msg
            }), 400
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        session.rollback()
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # Check if it's an enum validation error from SQLAlchemy
        if 'RoleLevel' in error_msg or 'not a valid' in error_msg.lower() or 'is not a valid' in error_msg.lower():
            return jsonify({
                'error': f'Invalid role_level value. Valid values are: JR, MID, SR, LEAD, PRINCIPAL',
                'details': error_msg,
                'hint': 'This might be a database schema issue. Try reinitializing the database.',
                'traceback': error_trace
            }), 400
        
        # Log the full error for debugging
        print(f"ERROR in create_employee: {error_msg}")
        print(f"TRACEBACK: {error_trace}")
        
        return jsonify({
            'error': error_msg,
            'traceback': error_trace,
            'hint': 'Check the backend console for full error details'
        }), 500
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
                    try:
                        role_level_enum = parse_role_level(data[field])
                        setattr(employee, field, str(role_level_enum.value))  # Store enum value as plain string
                    except ValueError as e:
                        return jsonify({'error': str(e)}), 400
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
            'allocation_percentage': alloc.allocation_percentage if hasattr(alloc, 'allocation_percentage') else (alloc.utilization if alloc.utilization else 100),
            'billable_percentage': alloc.billable_percentage if hasattr(alloc, 'billable_percentage') else 100,
            'utilization': alloc.allocation_percentage if hasattr(alloc, 'allocation_percentage') else (alloc.utilization if alloc.utilization else 100)  # Backward compatibility
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
                'role_level': employee.role_level if employee.role_level else None,  # Already a string from DB
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

@bp.route('/<int:employee_id>/allocation-check', methods=['POST'])
def check_employee_allocation(employee_id):
    """
    Check employee's current allocation state for validation
    This queries the current DB state to ensure accurate validation.
    
    Input: {
        'internal_allocation_percentage': int (preferred),
        'allocation_percentage': int (fallback if internal_allocation_percentage not provided),
        'start_date': 'YYYY-MM-DD',
        'end_date': 'YYYY-MM-DD' (optional),
        'exclude_allocation_id': int (optional, for updates)
    }
    Output: {
        'is_valid': bool,
        'current_total': int,
        'would_be_total': int,
        'error_message': str (if invalid),
        'employee_name': str
    }
    """
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        # Use internal_allocation_percentage if provided, otherwise fallback to allocation_percentage
        internal_allocation_percentage = data.get('internal_allocation_percentage')
        if internal_allocation_percentage is None:
            internal_allocation_percentage = data.get('allocation_percentage', 100)
        internal_allocation_percentage = int(internal_allocation_percentage)
        
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = None
        if data.get('end_date'):
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        exclude_allocation_id = data.get('exclude_allocation_id')
        
        # Query current DB state for overlapping allocations
        query = session.query(Allocation).filter(Allocation.emp_id == employee_id)
        if exclude_allocation_id:
            query = query.filter(Allocation.id != exclude_allocation_id)
        
        # Find allocations that overlap with the new date range
        overlapping_allocations = []
        for alloc in query.all():
            alloc_start = alloc.start_date
            alloc_end = alloc.end_date if alloc.end_date else date(2099, 12, 31)
            new_end = end_date if end_date else date(2099, 12, 31)
            if alloc_start <= new_end and start_date <= alloc_end:
                overlapping_allocations.append(alloc)
        
        # Calculate current total from DB using internal_allocation_percentage
        current_total = 0
        for alloc in overlapping_allocations:
            try:
                # Try to get internal_allocation_percentage (primary field)
                alloc_pct = getattr(alloc, 'internal_allocation_percentage', None)
                if alloc_pct is None:
                    # Fallback to allocation_percentage
                    alloc_pct = getattr(alloc, 'allocation_percentage', None)
                    if alloc_pct is None:
                        # Fallback to utilization
                        alloc_pct = getattr(alloc, 'utilization', 100) or 100
                current_total += alloc_pct
            except (AttributeError, TypeError):
                current_total += 100
        
        # If internal allocation percentage is 0%, it doesn't count towards total (always valid)
        if internal_allocation_percentage == 0:
            would_be_total = current_total  # 0% doesn't add to total
            is_valid = True
            error_msg = None
        else:
            would_be_total = current_total + internal_allocation_percentage
            
            # Use the validation function to check (which also queries DB)
            is_valid, error_msg = validate_allocation_percentage(
                session,
                employee_id,
                internal_allocation_percentage,
                start_date,
                end_date,
                exclude_allocation_id
            )
        
        return jsonify({
            'is_valid': is_valid,
            'current_total': current_total,
            'would_be_total': would_be_total,
            'error_message': error_msg if not is_valid else None,
            'employee_name': f"{employee.first_name} {employee.last_name}"
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:employee_id>/feedback', methods=['POST'])
def create_employee_feedback(employee_id):
    """Create performance feedback for an employee"""
    session = db_tool.Session()
    try:
        employee = session.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        proj_id = data.get('project_id')
        rating = data.get('rating')
        feedback = data.get('feedback')
        tags = data.get('tags', '')
        
        if not proj_id or not rating or not feedback:
            return jsonify({'error': 'project_id, rating, and feedback are required'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Verify project exists
        from models import Project
        project = session.query(Project).filter(Project.id == proj_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Create feedback
        feedback_obj = Feedback360(
            emp_id=employee_id,
            proj_id=proj_id,
            rating=rating,
            feedback=feedback,
            tags=tags
        )
        session.add(feedback_obj)
        session.commit()
        
        return jsonify({
            'message': 'Feedback created successfully',
            'feedback': {
                'id': feedback_obj.id,
                'project_name': project.project_name,
                'rating': feedback_obj.rating,
                'feedback': feedback_obj.feedback,
                'tags': feedback_obj.tags
            }
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()