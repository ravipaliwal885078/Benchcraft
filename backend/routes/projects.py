"""
Project Management Routes
/projects - CRUD for projects
"""
from flask import Blueprint, request, jsonify
from tools.sql_db import SQLDatabaseTool
from tools.vector_db import ChromaSearchTool
from models import Project, ProjectStatus, ProjectType, ProjectRoleRequirements, Allocation, Employee, AllocationFinancial
from datetime import datetime, date
from utils.allocation_validator import validate_allocation_percentage

bp = Blueprint('projects', __name__)
db_tool = SQLDatabaseTool()
vector_tool = ChromaSearchTool()

@bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    session = db_tool.Session()
    try:
        all_projects = session.query(Project).all()
        projects = []
        for p in all_projects:
            # Calculate budget consumed from allocations
            budget_consumed = 0
            try:
                for alloc in p.allocations:
                    if alloc.billing_rate:
                        # Simple calculation: billing_rate * allocation_percentage / 100
                        # This is a simplified calculation - in production, you'd calculate based on hours worked
                        alloc_pct = getattr(alloc, 'allocation_percentage', None) or getattr(alloc, 'utilization', 100) or 100
                        billable_pct = getattr(alloc, 'billable_percentage', None) or 100
                        # Estimate monthly cost: billing_rate * 160 hours * allocation% * billable%
                        monthly_cost = alloc.billing_rate * 160 * (alloc_pct / 100) * (billable_pct / 100)
                        budget_consumed += monthly_cost
            except Exception:
                # If calculation fails, use 0
                budget_consumed = 0
            
            projects.append({
                'id': p.id,
                'client_name': p.client_name,
                'project_name': p.project_name,
                'description': p.description,
                'budget_cap': p.budget_cap,
                'budget_consumed': round(budget_consumed, 2),
                'start_date': p.start_date.isoformat() if p.start_date else None,
                'end_date': p.end_date.isoformat() if p.end_date else None,
                'status': p.status.value if p.status else None,
                'probability': p.probability,
                'tech_stack': p.tech_stack
            })
        
        return jsonify({'projects': projects})
    finally:
        session.close()

@bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project with wizard data (includes role requirements and team allotment)"""
    data = request.get_json()
    session = db_tool.Session()
    try:
        # Validate required fields
        required_fields = ['client_name', 'project_name', 'description', 'budget_cap']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse dates
        start_date = None
        if data.get('start_date'):
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        end_date = None
        if data.get('end_date'):
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Parse status
        status = ProjectStatus.PIPELINE
        if data.get('status'):
            try:
                status = ProjectStatus[data['status']]
            except KeyError:
                return jsonify({'error': f'Invalid status: {data["status"]}'}), 400
        
        # Parse project_type
        project_type = None
        if data.get('project_type'):
            try:
                project_type = ProjectType[data['project_type']]
            except KeyError:
                return jsonify({'error': f'Invalid project_type: {data["project_type"]}'}), 400
        
        # Create project (without project_code first, will generate after commit)
        project = Project(
            client_name=data['client_name'],
            project_name=data['project_name'],
            description=data['description'],
            budget_cap=float(data['budget_cap']),
            billing_currency=data.get('billing_currency', 'USD'),
            project_type=project_type,
            industry_domain=data.get('industry_domain'),
            start_date=start_date,
            end_date=end_date,
            status=status,
            probability=int(data.get('probability', 0)),
            tech_stack=data.get('tech_stack', '')
        )
        
        session.add(project)
        session.flush()  # Flush to get the project.id
        
        # Generate project_code: PROJ-<Year>-<PrimaryKey>
        current_year = datetime.now().year
        project.project_code = f"PROJ-{current_year}-{project.id}"
        
        # Create role requirements if provided (Step 2: Team Structure)
        role_requirements_data = data.get('role_requirements', [])
        for role_req in role_requirements_data:
            role_req_obj = ProjectRoleRequirements(
                proj_id=project.id,
                role_name=role_req['role_name'],
                required_count=int(role_req['required_count']),
                utilization_percentage=int(role_req['utilization_percentage'])
            )
            session.add(role_req_obj)
        
        # Create allocations if provided (Step 3: Team Allotment)
        allocations_data = data.get('allocations', [])
        for alloc_data in allocations_data:
            alloc_start_date = datetime.strptime(alloc_data['start_date'], '%Y-%m-%d').date() if alloc_data.get('start_date') else start_date
            alloc_end_date = datetime.strptime(alloc_data['end_date'], '%Y-%m-%d').date() if alloc_data.get('end_date') else end_date
            
            allocation = Allocation(
                emp_id=int(alloc_data['employee_id']),
                proj_id=project.id,
                start_date=alloc_start_date,
                end_date=alloc_end_date,
                allocation_percentage=int(alloc_data.get('allocation_percentage', 100)),
                billable_percentage=int(alloc_data.get('billable_percentage', 100)),
                billing_rate=float(alloc_data['billing_rate']) if alloc_data.get('billing_rate') else None,
                is_revealed=False
            )
            session.add(allocation)
        
        session.commit()
        session.refresh(project)
        
        return jsonify({
            'message': 'Project created successfully',
            'project': {
                'id': project.id,
                'project_code': project.project_code,
                'client_name': project.client_name,
                'project_name': project.project_name,
                'description': project.description,
                'budget_cap': project.budget_cap,
                'billing_currency': project.billing_currency,
                'project_type': project.project_type.value if project.project_type else None,
                'industry_domain': project.industry_domain,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'status': project.status.value if project.status else None,
                'probability': project.probability,
                'tech_stack': project.tech_stack
            }
        }), 201
    except ValueError as e:
        session.rollback()
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    finally:
        session.close()

@bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Get detailed project view with allocations and team
    """
    session = db_tool.Session()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get allocations and team members
        # Handle cases where new columns might not exist in database yet
        allocations = []
        try:
            # Try to access allocations - this might fail if columns don't exist
            for alloc in project.allocations:
                # Safely get allocation_percentage with fallback to utilization
                allocation_pct = 100  # default
                try:
                    # Try to access the new field
                    allocation_pct = alloc.allocation_percentage
                    if allocation_pct is None:
                        allocation_pct = 100
                except (AttributeError, KeyError):
                    # Column doesn't exist, try utilization
                    try:
                        allocation_pct = alloc.utilization if alloc.utilization is not None else 100
                    except (AttributeError, KeyError):
                        allocation_pct = 100
                
                # Safely get billable_percentage
                billable_pct = 100  # default
                try:
                    billable_pct = alloc.billable_percentage
                    if billable_pct is None:
                        billable_pct = 100
                except (AttributeError, KeyError):
                    billable_pct = 100
                
                allocations.append({
                    'id': alloc.id,
                    'employee_id': alloc.employee.id,
                    'employee_uuid': alloc.employee.uuid,
                    'first_name': alloc.employee.first_name,
                    'last_name': alloc.employee.last_name,
                    'role_level': alloc.employee.role_level if alloc.employee.role_level else None,  # role_level is stored as string
                    'start_date': alloc.start_date.isoformat(),
                    'end_date': alloc.end_date.isoformat() if alloc.end_date else None,
                    'billing_rate': alloc.billing_rate,
                    'allocation_percentage': allocation_pct,
                    'billable_percentage': billable_pct,
                    'utilization': allocation_pct,  # Backward compatibility
                    'is_revealed': alloc.is_revealed
                })
        except Exception as e:
            # If there's an error accessing allocations (e.g., missing columns in DB)
            # Try to query allocations manually with only existing columns
            import traceback
            print(f"Warning: Error loading allocations via relationship: {e}")
            print(traceback.format_exc())
            
            # Fallback: Query allocations directly with basic columns only
            try:
                from models import Allocation
                allocs = session.query(Allocation).filter(Allocation.proj_id == project_id).all()
                for alloc in allocs:
                    # Get utilization if available, otherwise default to 100
                    utilization = getattr(alloc, 'utilization', 100) or 100
                    allocations.append({
                        'id': alloc.id,
                        'employee_id': alloc.emp_id,
                        'employee_uuid': alloc.employee.uuid if alloc.employee else None,
                        'first_name': alloc.employee.first_name if alloc.employee else 'Unknown',
                        'last_name': alloc.employee.last_name if alloc.employee else '',
                        'role_level': alloc.employee.role_level if alloc.employee and alloc.employee.role_level else None,
                        'start_date': alloc.start_date.isoformat() if alloc.start_date else None,
                        'end_date': alloc.end_date.isoformat() if alloc.end_date else None,
                        'billing_rate': alloc.billing_rate,
                        'allocation_percentage': utilization,
                        'billable_percentage': 100,
                        'utilization': utilization,
                        'is_revealed': alloc.is_revealed
                    })
            except Exception as fallback_error:
                print(f"Error in fallback allocation query: {fallback_error}")
                allocations = []

        # Get feedback for this project
        feedbacks = [{
            'id': fb.id,
            'employee_name': f"{fb.employee.first_name} {fb.employee.last_name}",
            'rating': fb.rating,
            'feedback': fb.feedback,
            'tags': fb.tags
        } for fb in project.feedbacks]

        # Calculate project metrics
        total_allocated = len([a for a in allocations if not a['end_date'] or a['end_date'] >= datetime.now().date().isoformat()])
        avg_utilization = sum(a['allocation_percentage'] or 100 for a in allocations) / len(allocations) if allocations else 0
        
        # Calculate budget utilized based on team members' billable hours
        total_budget_used = 0.0
        today = date.today()
        
        for alloc_data in allocations:
            billing_rate = alloc_data.get('billing_rate')
            # Handle None, 0, or missing billing_rate
            if billing_rate is None or billing_rate == 0:
                # Try to get billing rate from AllocationFinancial if available
                try:
                    alloc_id = alloc_data.get('id')
                    if alloc_id:
                        financial = session.query(AllocationFinancial).filter(
                            AllocationFinancial.allocation_id == alloc_id
                        ).first()
                        if financial and financial.billing_rate:
                            billing_rate = financial.billing_rate
                except Exception:
                    pass
                
                # If still no billing rate, try to get from employee's rate card
                if (billing_rate is None or billing_rate == 0):
                    try:
                        from models import RateCard, RateType
                        employee_id = alloc_data.get('employee_id')
                        if employee_id:
                            # Try to get base rate card for employee
                            rate_card = session.query(RateCard).filter(
                                RateCard.emp_id == employee_id,
                                RateCard.domain_id.is_(None),
                                RateCard.rate_type == RateType.BASE,
                                RateCard.is_active == True
                            ).order_by(RateCard.effective_date.desc()).first()
                            
                            if rate_card and rate_card.hourly_rate:
                                billing_rate = rate_card.hourly_rate
                    except Exception:
                        pass
                
                # If still no billing rate, skip this allocation
                if billing_rate is None or billing_rate == 0:
                    continue
            
            if billing_rate <= 0:
                continue
            
            # Get allocation and billable percentages
            allocation_pct = alloc_data.get('allocation_percentage', 100) or 100
            billable_pct = alloc_data.get('billable_percentage', 100) or 100
            
            # Calculate time period
            start_date_str = alloc_data.get('start_date')
            end_date_str = alloc_data.get('end_date')
            
            if not start_date_str:
                continue
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
            except (ValueError, TypeError):
                continue
            
            # For budget calculation, we want to calculate based on actual time worked
            # If start_date is in the future, use start_date as the calculation start
            # If end_date is in the future or None, use today as the calculation end
            calc_start_date = start_date if start_date <= today else today
            calc_end_date = end_date if (end_date and end_date <= today) else today
            
            # If start_date is in the future, we haven't incurred any costs yet
            if start_date > today:
                continue
            
            # Use calculated dates for the period calculation
            start_date = calc_start_date
            end_date = calc_end_date
            
            # Calculate total days in the allocation period
            total_days = (end_date - start_date).days + 1
            if total_days <= 0:
                continue
            
            # Calculate working days (assuming 5 working days per week)
            # Simplified: approximate working days = total_days * 5/7
            working_days = total_days * 5 / 7
            
            # Calculate total working hours (8 hours per working day)
            # Assuming 160 working hours per month (8 hours * 20 days)
            working_hours = working_days * 8  # 8 hours per day
            
            # Calculate billable hours based on allocation and billable percentages
            # billable_hours = working_hours * (allocation_percentage / 100) * (billable_percentage / 100)
            # Example: 160 hours/month, 50% allocation, 100% billable = 80 billable hours
            billable_hours = working_hours * (allocation_pct / 100.0) * (billable_pct / 100.0)
            
            # Calculate cost: billable_hours * billing_rate
            member_cost = billable_hours * billing_rate
            total_budget_used += member_cost
            
            # Debug logging (can be removed in production)
            print(f"Budget calc for allocation {alloc_data.get('id')}: "
                  f"start={start_date_str}, end={end_date_str or 'ongoing'}, "
                  f"days={total_days}, working_hours={working_hours:.2f}, "
                  f"billable_hours={billable_hours:.2f}, rate=${billing_rate}, "
                  f"cost=${member_cost:.2f}")
        
        # Debug: Log if no budget was calculated
        if total_budget_used == 0 and len(allocations) > 0:
            print(f"WARNING: Budget calculated as $0.00 for project {project_id} with {len(allocations)} allocations")
            for alloc_data in allocations:
                print(f"  Allocation {alloc_data.get('id')}: billing_rate={alloc_data.get('billing_rate')}, "
                      f"start_date={alloc_data.get('start_date')}, end_date={alloc_data.get('end_date')}")

        return jsonify({
            'project': {
                'id': project.id,
                'client_name': project.client_name,
                'project_name': project.project_name,
                'description': project.description,
                'budget_cap': project.budget_cap,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'status': project.status.value if project.status else None,
                'probability': project.probability,
                'tech_stack': project.tech_stack
            },
            'team': allocations,
            'feedbacks': feedbacks,
            'metrics': {
                'total_team_members': total_allocated,
                'budget_utilized': round(total_budget_used, 2),
                'budget_remaining': round(max(0, project.budget_cap - total_budget_used), 2),
                'avg_utilization': round(avg_utilization, 1),
                'total_allocations': len(allocations)
            }
        })
    finally:
        session.close()

@bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update project details"""
    session = db_tool.Session()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'client_name' in data:
            project.client_name = data['client_name']
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'description' in data:
            project.description = data['description']
        if 'budget_cap' in data:
            project.budget_cap = float(data['budget_cap'])
        if 'start_date' in data and data['start_date']:
            project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        # Track if end_date changed
        old_end_date = project.end_date
        if 'end_date' in data:
            if data['end_date']:
                project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            else:
                project.end_date = None
        
        # If project end_date was updated and is not None, sync all team member end dates
        if 'end_date' in data and project.end_date is not None:
            # Update all allocations for this project to match the project end_date
            for allocation in project.allocations:
                # Only update if allocation doesn't have an end_date or if it's after the project end_date
                if allocation.end_date is None or allocation.end_date > project.end_date:
                    allocation.end_date = project.end_date
        
        if 'status' in data:
            try:
                project.status = ProjectStatus[data['status']]
            except KeyError:
                return jsonify({'error': f'Invalid status: {data["status"]}'}), 400
        if 'probability' in data:
            project.probability = int(data['probability'])
        if 'tech_stack' in data:
            project.tech_stack = data['tech_stack']
        
        session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': {
                'id': project.id,
                'client_name': project.client_name,
                'project_name': project.project_name,
                'description': project.description,
                'budget_cap': project.budget_cap,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'status': project.status.value if project.status else None,
                'probability': project.probability,
                'tech_stack': project.tech_stack
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/projects/<int:project_id>/team', methods=['POST'])
def update_project_team(project_id):
    """
    Update project team allocations
    Input: {
        'allocations': [
            {
                'employee_id': int,
                'allocation_id': int (optional, for updates),
                'start_date': 'YYYY-MM-DD',
                'end_date': 'YYYY-MM-DD' (optional),
                'allocation_percentage': int (0-100),
                'billable_percentage': int (0-100),
                'billing_rate': float (optional)
            }
        ]
    }
    """
    session = db_tool.Session()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        allocations_data = data.get('allocations', [])
        
        if not allocations_data:
            return jsonify({'error': 'No allocations provided'}), 400
        
        updated_allocations = []
        
        for alloc_data in allocations_data:
            employee_id = alloc_data.get('employee_id')
            allocation_id = alloc_data.get('allocation_id')
            
            if not employee_id:
                return jsonify({'error': 'employee_id is required for each allocation'}), 400
            
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                return jsonify({'error': f'Employee {employee_id} not found'}), 404
            
            # Validate percentages
            allocation_percentage = alloc_data.get('allocation_percentage', 100)
            billable_percentage = alloc_data.get('billable_percentage', 100)
            
            if not (0 <= allocation_percentage <= 100):
                return jsonify({'error': 'allocation_percentage must be between 0 and 100'}), 400
            if not (0 <= billable_percentage <= 100):
                return jsonify({'error': 'billable_percentage must be between 0 and 100'}), 400
            
            # Parse dates
            start_date = datetime.strptime(alloc_data['start_date'], '%Y-%m-%d').date()
            end_date = None
            if alloc_data.get('end_date'):
                end_date = datetime.strptime(alloc_data['end_date'], '%Y-%m-%d').date()
            
            # Validate total allocation percentage doesn't exceed 100%
            is_valid, error_msg = validate_allocation_percentage(
                session, 
                employee_id, 
                allocation_percentage, 
                start_date, 
                end_date,
                exclude_allocation_id=allocation_id  # Exclude current allocation if updating
            )
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            if allocation_id:
                # Update existing allocation
                allocation = session.query(Allocation).filter(
                    Allocation.id == allocation_id,
                    Allocation.proj_id == project_id
                ).first()
                
                if not allocation:
                    return jsonify({'error': f'Allocation {allocation_id} not found'}), 404
                
                allocation.start_date = start_date
                allocation.end_date = end_date
                allocation.allocation_percentage = allocation_percentage
                allocation.billable_percentage = billable_percentage
                if 'billing_rate' in alloc_data:
                    allocation.billing_rate = float(alloc_data['billing_rate']) if alloc_data['billing_rate'] else None
            else:
                # Create new allocation
                allocation = Allocation(
                    emp_id=employee_id,
                    proj_id=project_id,
                    start_date=start_date,
                    end_date=end_date,
                    allocation_percentage=allocation_percentage,
                    billable_percentage=billable_percentage,
                    billing_rate=float(alloc_data['billing_rate']) if alloc_data.get('billing_rate') else None,
                    is_revealed=False
                )
                session.add(allocation)
            
            updated_allocations.append({
                'id': allocation.id if allocation_id else None,  # Will be set after commit
                'employee_id': employee_id,
                'allocation_percentage': allocation_percentage,
                'billable_percentage': billable_percentage
            })
        
        session.commit()
        
        # Refresh allocations to get IDs
        for i, alloc_data in enumerate(allocations_data):
            if not alloc_data.get('allocation_id'):
                # Find the newly created allocation
                new_alloc = session.query(Allocation).filter(
                    Allocation.emp_id == alloc_data['employee_id'],
                    Allocation.proj_id == project_id,
                    Allocation.start_date == datetime.strptime(alloc_data['start_date'], '%Y-%m-%d').date()
                ).order_by(Allocation.id.desc()).first()
                if new_alloc:
                    updated_allocations[i]['id'] = new_alloc.id
        
        return jsonify({
            'message': 'Project team updated successfully',
            'allocations': updated_allocations
        })
    except ValueError as e:
        session.rollback()
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/projects/<int:project_id>/team/<int:allocation_id>', methods=['DELETE'])
def remove_team_member(project_id, allocation_id):
    """Remove team member from project"""
    session = db_tool.Session()
    try:
        allocation = session.query(Allocation).filter(
            Allocation.id == allocation_id,
            Allocation.proj_id == project_id
        ).first()
        
        if not allocation:
            return jsonify({'error': 'Allocation not found'}), 404
        
        # Explicitly delete related AllocationFinancial if it exists
        # Use raw SQL to avoid schema mismatch issues with missing columns
        # This ensures proper cleanup even if cascade doesn't work as expected
        from sqlalchemy import text
        try:
            session.execute(
                text("DELETE FROM allocation_financials WHERE allocation_id = :allocation_id"),
                {"allocation_id": allocation_id}
            )
            session.flush()  # Flush to ensure financial is deleted before allocation
        except Exception as e:
            # If deletion fails (e.g., table doesn't exist or column issues), log and continue
            print(f"Warning: Could not delete AllocationFinancial: {e}")
            # Continue with allocation deletion anyway
        
        # Delete the allocation
        session.delete(allocation)
        session.commit()
        
        return jsonify({'message': 'Team member removed successfully'})
    except Exception as e:
        session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error removing team member: {error_details}")
        # Return error message that can be displayed to user
        error_message = str(e)
        if 'FOREIGN KEY constraint' in error_message or 'constraint' in error_message.lower():
            error_message = f"Database constraint error: {error_message}"
        return jsonify({'error': error_message, 'details': error_details}), 500
    finally:
        session.close()

@bp.route('/projects/<int:project_id>/feedback', methods=['POST'])
def create_project_feedback(project_id):
    """Create performance feedback for a project team member"""
    session = db_tool.Session()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        emp_id = data.get('employee_id')
        rating = data.get('rating')
        feedback = data.get('feedback')
        tags = data.get('tags', '')
        
        if not emp_id or not rating or not feedback:
            return jsonify({'error': 'employee_id, rating, and feedback are required'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Verify employee exists
        employee = session.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Create feedback
        from models import Feedback360
        feedback_obj = Feedback360(
            emp_id=emp_id,
            proj_id=project_id,
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
                'employee_name': f"{employee.first_name} {employee.last_name}",
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
