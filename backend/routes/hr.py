"""
HR Verification and Profile Activation Routes
"""
from flask import Blueprint, request, jsonify
from tools.sql_db import SQLDatabaseTool
from models import (
    Employee, EmployeeStatus, Allocation, Project, RateCard, 
    AllocationFinancial, PriorityScoring, EmployeeDomain, Domain, RateType
)
from datetime import date, datetime, timedelta
from sqlalchemy import and_, or_, func, text, inspect

bp = Blueprint('hr', __name__)
db_tool = SQLDatabaseTool()

@bp.route('/test', methods=['GET'])
def test_route():
    """Test route to verify HR blueprint is working"""
    return jsonify({'message': 'HR routes are working', 'route': '/api/v1/hr/test'})

@bp.route('/init-db', methods=['POST'])
def init_database():
    """Initialize database tables for financials and domains, and add missing columns"""
    try:
        from models import Base
        from sqlalchemy import create_engine, text, inspect
        from config import Config
        
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        
        # Create all new tables
        Base.metadata.create_all(engine)
        
        # Add missing columns to existing tables
        columns_added = []
        with engine.connect() as conn:
            inspector = inspect(engine)
            
            # Check if allocations table has rate_card_id column
            if 'allocations' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('allocations')]
                if 'rate_card_id' not in columns:
                    try:
                        conn.execute(text('ALTER TABLE allocations ADD COLUMN rate_card_id INTEGER'))
                        conn.commit()
                        columns_added.append('allocations.rate_card_id')
                    except Exception as e:
                        # Column might already exist or other error
                        pass
        
        return jsonify({
            'message': 'Database tables initialized successfully',
            'tables_created': [
                'domains', 'employee_domains', 'project_domains', 
                'rate_cards', 'financial_metrics', 'allocation_financials',
                'priority_scoring', 'project_rate_requirements'
            ],
            'columns_added': columns_added if columns_added else ['No new columns needed']
        })
    except Exception as e:
        return jsonify({'error': f'Failed to initialize database: {str(e)}'}), 500

@bp.route('/pending', methods=['GET'])
def get_pending_profiles():
    session = db_tool.Session()
    try:
        employees = session.query(Employee).filter(Employee.status == EmployeeStatus.BENCH).all()
        result = [
            {
                'id': emp.id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'status': emp.status.value if emp.status and hasattr(emp.status, 'value') else str(emp.status) if emp.status else None
            }
            for emp in employees
        ]
        return jsonify(result)
    finally:
        session.close()

@bp.route('/verify/<int:emp_id>', methods=['POST'])
def verify_profile(emp_id):
    session = db_tool.Session()
    try:
        emp = session.query(Employee).get(emp_id)
        if not emp:
            return jsonify({'error': 'Employee not found'}), 404
        emp.status = EmployeeStatus.ALLOCATED
        session.commit()
        return jsonify({'message': 'Profile verified and activated', 'id': emp.id})
    finally:
        session.close()


def calculate_hourly_cost(employee):
    """Calculate employee hourly cost from monthly CTC"""
    # Assuming 160 working hours per month (8 hours * 20 days)
    if employee.ctc_monthly:
        return employee.ctc_monthly / 160.0
    return 0.0


def calculate_gross_margin(billing_rate, cost_rate):
    """Calculate gross margin percentage"""
    if billing_rate and billing_rate > 0:
        margin = ((billing_rate - cost_rate) / billing_rate) * 100
        return round(margin, 2)
    return 0.0


def get_current_rate_card(employee, project_domain_id=None, session=None):
    """Get the most appropriate rate card for an employee"""
    if not session:
        session = db_tool.Session()
        should_close = True
    else:
        should_close = False
    
    try:
        # Check if RateCard table exists by trying a simple query
        try:
            # First try domain-specific rate if project_domain_id is provided
            if project_domain_id:
                domain_rate = session.query(RateCard).filter(
                    and_(
                        RateCard.emp_id == employee.id,
                        RateCard.domain_id == project_domain_id,
                        RateCard.is_active == True,
                        or_(
                            RateCard.expiry_date.is_(None),
                            RateCard.expiry_date >= date.today()
                        )
                    )
                ).order_by(RateCard.effective_date.desc()).first()
                
                if domain_rate:
                    return domain_rate
            
            # Fall back to base rate
            base_rate = session.query(RateCard).filter(
                and_(
                    RateCard.emp_id == employee.id,
                    RateCard.domain_id.is_(None),
                    RateCard.rate_type == RateType.BASE,
                    RateCard.is_active == True,
                    or_(
                        RateCard.expiry_date.is_(None),
                        RateCard.expiry_date >= date.today()
                    )
                )
            ).order_by(RateCard.effective_date.desc()).first()
            
            return base_rate
        except Exception:
            # RateCard table doesn't exist yet
            return None
    finally:
        if should_close:
            session.close()


@bp.route('/allocation-report', methods=['GET'])
def get_allocation_report():
    """
    HR/Project Allocation Manager Report
    Returns employee allocation details with financial metrics for proactive planning
    Query params: 
    - forecast_days: Number of days to look ahead (default: 30)
    - include_bench: Include employees on bench (default: true)
    """
    try:
        session = db_tool.Session()
    except Exception as e:
        return jsonify({'error': f'Database connection error: {str(e)}'}), 500
    
    try:
        forecast_days = int(request.args.get('forecast_days', 30))
        include_bench = request.args.get('include_bench', 'true').lower() == 'true'
        
        today = date.today()
        forecast_date = today + timedelta(days=forecast_days)
        
        # VALIDATION: Check if rate_card_id column exists in allocations table
        inspector = inspect(session.bind)
        rate_card_id_exists = False
        if 'allocations' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('allocations')]
            rate_card_id_exists = 'rate_card_id' in columns
            print(f"Database validation: rate_card_id column exists = {rate_card_id_exists}")
        
        if not rate_card_id_exists:
            session.close()
            return jsonify({
                'error': 'Database schema needs to be updated. The allocations table is missing the rate_card_id column.',
                'solution': 'Please run the migration script to add the missing column',
                'migration_script': 'python backend/migrate_add_rate_card_id.py',
                'api_endpoint': 'POST /api/v1/hr/init-db',
                'instructions': 'Run: cd backend && python migrate_add_rate_card_id.py'
            }), 500
        
        # Get all employees
        try:
            query = session.query(Employee)
            if not include_bench:
                query = query.filter(Employee.status != EmployeeStatus.BENCH)
            
            employees = query.all()
            print(f"Found {len(employees)} employees to process")
        except Exception as db_error:
            error_msg = str(db_error)
            session.close()
            return jsonify({
                'error': f'Database query error: {error_msg}',
                'solution': 'Please check database connection and schema'
            }), 500
        
        report_data = []
        
        for employee in employees:
            try:
                # Get current allocation (column exists, so use normal query)
                current_allocation = session.query(Allocation).filter(
                    and_(
                        Allocation.emp_id == employee.id,
                        Allocation.start_date <= today,
                        or_(
                            Allocation.end_date.is_(None),
                            Allocation.end_date >= today
                        )
                    )
                ).first()
                
                # Get upcoming allocations (for proactive planning)
                upcoming_allocations = session.query(Allocation).filter(
                    and_(
                        Allocation.emp_id == employee.id,
                        Allocation.start_date > today,
                        Allocation.start_date <= forecast_date
                    )
                ).all()
                
                # Calculate current hourly rate
                hourly_cost = calculate_hourly_cost(employee)
                current_rate_card = None
                current_hourly_rate = None
                
                if current_allocation:
                    # Get rate card used in allocation (handle if column doesn't exist)
                    try:
                        # Check if rate_card_id column exists in the allocation
                        rate_card_id = None
                        try:
                            rate_card_id = getattr(current_allocation, 'rate_card_id', None)
                        except AttributeError:
                            # Column doesn't exist in database yet
                            pass
                        
                        if rate_card_id:
                            try:
                                current_rate_card = session.query(RateCard).filter(
                                    RateCard.id == rate_card_id
                                ).first()
                            except Exception:
                                # RateCard table doesn't exist
                                current_rate_card = None
                        
                        # If no rate card linked, try to find appropriate one
                        if not current_rate_card and current_allocation.project:
                            # Try to get project domain
                            try:
                                project_domains = session.query(EmployeeDomain).join(Domain).filter(
                                    EmployeeDomain.emp_id == employee.id
                                ).all()
                                
                                if project_domains:
                                    # Use first domain for now (could be enhanced)
                                    current_rate_card = get_current_rate_card(
                                        employee, 
                                        project_domains[0].domain_id if project_domains else None,
                                        session
                                    )
                            except Exception:
                                # Tables don't exist yet, skip domain lookup
                                pass
                        
                        # Fallback to base rate
                        if not current_rate_card:
                            try:
                                current_rate_card = get_current_rate_card(employee, None, session)
                            except Exception:
                                # Rate card table doesn't exist yet
                                pass
                        
                        if current_rate_card:
                            current_hourly_rate = current_rate_card.hourly_rate
                    except Exception:
                        # RateCard table doesn't exist yet, use billing_rate from allocation
                        pass
                    
                    # Use billing_rate as fallback
                    if not current_hourly_rate and current_allocation.billing_rate:
                        current_hourly_rate = current_allocation.billing_rate
                    
                    # Get allocation financials if available (handle if table doesn't exist)
                    allocation_financial = None
                    try:
                        allocation_financial = session.query(AllocationFinancial).filter(
                            AllocationFinancial.allocation_id == current_allocation.id
                        ).first()
                    except Exception:
                        # AllocationFinancial table doesn't exist yet
                        pass
                    
                    # Calculate gross margin
                    if current_hourly_rate and hourly_cost:
                        gross_margin_pct = calculate_gross_margin(current_hourly_rate, hourly_cost)
                        gross_profit_per_hour = current_hourly_rate - hourly_cost
                    else:
                        gross_margin_pct = 0.0
                        gross_profit_per_hour = 0.0
                    
                    # Calculate alignment period
                    alignment_start = current_allocation.start_date
                    alignment_end = current_allocation.end_date if current_allocation.end_date else None
                    alignment_days = None
                    if alignment_end:
                        alignment_days = (alignment_end - alignment_start).days
                    
                    # Project details
                    project = current_allocation.project
                    project_name = project.project_name if project else "N/A"
                    client_name = project.client_name if project else "N/A"
                else:
                    # Employee on bench or not allocated
                    project_name = None
                    client_name = None
                    alignment_start = None
                    alignment_end = None
                    alignment_days = None
                    gross_margin_pct = 0.0
                    gross_profit_per_hour = 0.0
                    allocation_financial = None
                    
                    # Still get base rate card for potential allocation (handle if table doesn't exist)
                    try:
                        current_rate_card = get_current_rate_card(employee, None, session)
                        if current_rate_card:
                            current_hourly_rate = current_rate_card.hourly_rate
                        else:
                            current_hourly_rate = None
                    except Exception:
                        # RateCard table doesn't exist yet
                        current_rate_card = None
                        current_hourly_rate = None
                
                # Get priority score (handle if table doesn't exist)
                priority_score = None
                try:
                    priority_score = session.query(PriorityScoring).filter(
                        PriorityScoring.emp_id == employee.id
                    ).first()
                except Exception:
                    # PriorityScoring table doesn't exist yet
                    pass
                
                # Get employee domains (handle if table doesn't exist)
                employee_domains = []
                try:
                    employee_domains = session.query(EmployeeDomain).join(Domain).filter(
                        EmployeeDomain.emp_id == employee.id
                    ).all()
                except Exception:
                    # EmployeeDomain or Domain tables don't exist yet
                    pass
                
                # Calculate availability status
                availability_status = "AVAILABLE"
                next_available_date = None
                if current_allocation and current_allocation.end_date:
                    if current_allocation.end_date > today:
                        availability_status = f"ALLOCATED_UNTIL_{current_allocation.end_date.isoformat()}"
                        next_available_date = current_allocation.end_date
                    else:
                        availability_status = "AVAILABLE"
                        next_available_date = today
                elif current_allocation and not current_allocation.end_date:
                    availability_status = "ALLOCATED_INDEFINITE"
                else:
                    availability_status = "ON_BENCH"
                    next_available_date = today
                
                # Check if employee will be available in forecast period
                will_be_available = False
                if next_available_date and next_available_date <= forecast_date:
                    will_be_available = True
                
                # Safely get employee attributes
                try:
                    employee_name = f"{employee.first_name or ''} {employee.last_name or ''}".strip()
                    employee_email = employee.email or 'N/A'
                    # Handle status - could be enum or string
                    if hasattr(employee.status, 'value'):
                        employee_status = employee.status.value
                    else:
                        employee_status = str(employee.status) if employee.status else None
                    # Handle role_level - now stored as string
                    employee_role = str(employee.role_level) if employee.role_level else None
                    employee_ctc = employee.ctc_monthly or 0.0
                    employee_currency = employee.currency or 'USD'
                except Exception as emp_attr_error:
                    print(f"Error accessing employee attributes for emp_id {employee.id}: {emp_attr_error}")
                    import traceback
                    print(traceback.format_exc())
                    employee_name = f"Employee {employee.id}"
                    employee_email = 'N/A'
                    employee_status = None
                    employee_role = None
                    employee_ctc = 0.0
                    employee_currency = 'USD'
                
                employee_data = {
                    'employee_id': employee.id,
                    'employee_name': employee_name,
                    'email': employee_email,
                    'status': employee_status,
                    'role_level': employee_role,
                    'ctc_monthly': employee_ctc,
                    'currency': employee_currency,
                    'hourly_cost': round(hourly_cost, 2),
                    
                    # Current Project Details
                    'current_project': {
                        'project_name': project_name,
                        'client_name': client_name,
                        'project_id': current_allocation.proj_id if current_allocation else None,
                        'start_date': alignment_start.isoformat() if alignment_start else None,
                        'end_date': alignment_end.isoformat() if alignment_end else None,
                        'alignment_period_days': alignment_days,
                        'utilization_percentage': current_allocation.utilization if current_allocation else None
                    },
                    
                    # Financial Metrics
                    'financials': {
                        'current_hourly_rate': round(current_hourly_rate, 2) if current_hourly_rate else None,
                        'hourly_cost': round(hourly_cost, 2),
                        'gross_profit_per_hour': round(gross_profit_per_hour, 2) if gross_profit_per_hour else 0.0,
                        'gross_margin_percentage': round(gross_margin_pct, 2) if gross_margin_pct else 0.0,
                        'rate_card_id': current_rate_card.id if current_rate_card else None,
                        'rate_card_type': current_rate_card.rate_type.value if current_rate_card and current_rate_card.rate_type and hasattr(current_rate_card.rate_type, 'value') else (str(current_rate_card.rate_type) if current_rate_card and current_rate_card.rate_type else None),
                        'estimated_monthly_revenue': round(current_hourly_rate * 160, 2) if current_hourly_rate else None,
                        'estimated_monthly_cost': round(hourly_cost * 160, 2),
                        'estimated_monthly_profit': round(gross_profit_per_hour * 160, 2) if current_hourly_rate and gross_profit_per_hour else None
                    },
                    
                    # Allocation Financials (if available)
                    'allocation_financials': {
                        'billed_hours': allocation_financial.billed_hours if allocation_financial else None,
                        'utilized_hours': allocation_financial.utilized_hours if allocation_financial else None,
                        'actual_revenue': allocation_financial.actual_revenue if allocation_financial else None,
                        'actual_cost': allocation_financial.actual_cost if allocation_financial else None,
                        'actual_gross_margin': allocation_financial.gross_margin_percentage if allocation_financial else None
                    } if allocation_financial else None,
                    
                    # Priority & Availability
                    'priority': {
                        'priority_score': round(priority_score.priority_score, 2) if priority_score and priority_score.priority_score else None,
                        'priority_tier': priority_score.priority_tier.value if priority_score and priority_score.priority_tier and hasattr(priority_score.priority_tier, 'value') else (str(priority_score.priority_tier) if priority_score and priority_score.priority_tier else None),
                        'base_rate_card_value': priority_score.base_rate_card_value if priority_score else None,
                        'max_domain_rate_value': priority_score.max_domain_rate_value if priority_score else None,
                        'days_on_bench': priority_score.days_on_bench if priority_score else None
                    },
                    
                    # Availability & Proactive Planning
                    'availability': {
                        'status': availability_status,
                        'next_available_date': next_available_date.isoformat() if next_available_date else None,
                        'will_be_available_in_forecast': will_be_available,
                        'forecast_days': forecast_days
                    },
                    
                    # Upcoming Allocations
                    'upcoming_allocations': [
                        {
                            'project_id': alloc.proj_id,
                            'project_name': alloc.project.project_name if alloc.project else None,
                            'start_date': alloc.start_date.isoformat(),
                            'end_date': alloc.end_date.isoformat() if alloc.end_date else None,
                            'billing_rate': alloc.billing_rate
                        }
                        for alloc in upcoming_allocations
                    ],
                    
                    # Employee Domains
                    'domains': [
                        {
                            'domain_name': ed.domain.domain_name if ed.domain else 'N/A',
                            'domain_type': ed.domain.domain_type.value if ed.domain and ed.domain.domain_type and hasattr(ed.domain.domain_type, 'value') else (str(ed.domain.domain_type) if ed.domain and ed.domain.domain_type else None),
                            'proficiency': ed.proficiency,
                            'years_experience': ed.years_of_experience,
                            'is_primary': ed.is_primary_domain
                        }
                        for ed in employee_domains
                    ] if employee_domains else []
                }
                
                report_data.append(employee_data)
            except Exception as emp_error:
                # Log error for this employee but continue with others
                print(f"Error processing employee {employee.id}: {str(emp_error)}")
                import traceback
                print(traceback.format_exc())
                # Add a minimal entry so the report doesn't break
                report_data.append({
                    'employee_id': employee.id,
                    'employee_name': f"Employee {employee.id}",
                    'email': 'Error loading',
                    'status': None,
                    'error': f'Error processing: {str(emp_error)}'
                })
                continue
        
        # Sort by priority score (highest first) or by gross profit
        try:
            report_data.sort(
                key=lambda x: (
                    x.get('priority', {}).get('priority_score') or 0,
                    x.get('financials', {}).get('gross_profit_per_hour') or 0
                ),
                reverse=True
            )
        except Exception as sort_error:
            # If sorting fails, just keep original order
            print(f"Warning: Failed to sort report data: {sort_error}")
        
        # Calculate summary safely
        total_allocated = len([e for e in report_data if e.get('current_project', {}).get('project_name')])
        total_on_bench = len([e for e in report_data if e.get('status') == 'BENCH'])
        total_available = len([e for e in report_data if e.get('availability', {}).get('will_be_available_in_forecast', False)])
        
        # Calculate average gross margin safely
        margins = [e.get('financials', {}).get('gross_margin_percentage') for e in report_data 
                  if e.get('financials', {}).get('gross_margin_percentage') is not None]
        avg_margin = round(sum(margins) / len(margins), 2) if margins else 0
        
        return jsonify({
            'report_date': today.isoformat(),
            'forecast_days': forecast_days,
            'forecast_date': forecast_date.isoformat(),
            'total_employees': len(report_data),
            'employees': report_data,
            'summary': {
                'total_allocated': total_allocated,
                'total_on_bench': total_on_bench,
                'total_available_in_forecast': total_available,
                'avg_gross_margin': avg_margin
            }
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        error_type = type(e).__name__
        
        # Log to console for debugging
        print(f"\n{'='*60}")
        print(f"ERROR in allocation report: {error_msg}")
        print(f"Error Type: {error_type}")
        print(f"{'='*60}")
        print(f"Full Traceback:\n{error_trace}")
        print(f"{'='*60}\n")
        
        # Return detailed error for debugging
        return jsonify({
            'error': error_msg,
            'error_type': error_type,
            'message': f'Error occurred: {error_msg}',
            'hint': 'Check Flask server console for full traceback'
        }), 500
    finally:
        session.close()
