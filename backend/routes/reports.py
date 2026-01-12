"""
Reporting & Analytics Dashboard Routes
Provides actionable insights across Projects, Employees, and Risks
"""
from flask import Blueprint, jsonify, request
from tools.sql_db import SQLDatabaseTool
from models import (
    Employee, EmployeeStatus, Allocation, Project, ProjectStatus,
    AllocationFinancial, RiskRegister, RiskType, RiskSeverity,
    EmployeeSkill, ProjectRoleRequirements, EmployeeDomain, Domain
)
from datetime import date, datetime, timedelta
from sqlalchemy import and_, or_, func, text, case
from sqlalchemy.orm import joinedload
from utils.employee_status import get_derived_employee_status

bp = Blueprint('reports', __name__)
db_tool = SQLDatabaseTool()


def calculate_hourly_cost(employee):
    """Calculate employee hourly cost from monthly CTC"""
    if employee.ctc_monthly:
        return employee.ctc_monthly / 160.0
    return 0.0


def get_internal_allocation_percentage(allocation):
    """Get internal allocation percentage with fallback"""
    if hasattr(allocation, 'internal_allocation_percentage') and allocation.internal_allocation_percentage is not None:
        return allocation.internal_allocation_percentage
    if hasattr(allocation, 'allocation_percentage') and allocation.allocation_percentage is not None:
        return allocation.allocation_percentage
    if hasattr(allocation, 'utilization') and allocation.utilization is not None:
        return allocation.utilization
    return 100


# ============================================================================
# EPIC 1: Project Intelligence & ROI Analysis
# ============================================================================

@bp.route('/projects/resource-critical', methods=['GET'])
def get_resource_critical_projects():
    """
    Story 1.1: Identify Projects Running Short on Resources
    Flags projects where remaining resource capacity < remaining time demand
    """
    session = db_tool.Session()
    try:
        today = date.today()
        threshold = float(request.args.get('threshold', 20))  # Default 20% buffer
        
        # Get active projects
        active_projects = session.query(Project).filter(
            Project.status == ProjectStatus.ACTIVE
        ).all()
        
        critical_projects = []
        
        for project in active_projects:
            # Calculate remaining duration
            if project.end_date:
                remaining_days = (project.end_date - today).days
                if remaining_days <= 0:
                    continue
            else:
                # Ongoing project - assume 30 days for calculation
                remaining_days = 30
            
            # Get all allocations for this project
            allocations = session.query(Allocation).filter(
                Allocation.proj_id == project.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            # Calculate total allocated capacity (sum of internal_allocation_percentage)
            total_allocated = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            
            # Calculate consumed capacity (simplified: based on time elapsed)
            if project.start_date:
                elapsed_days = (today - project.start_date).days
                total_days = (project.end_date - project.start_date).days if project.end_date else elapsed_days + remaining_days
                if total_days > 0:
                    consumed_pct = (elapsed_days / total_days) * 100
                else:
                    consumed_pct = 0
            else:
                consumed_pct = 0
            
            # Calculate remaining capacity
            remaining_capacity = total_allocated - (total_allocated * consumed_pct / 100)
            
            # Calculate demand (simplified: assume 100% needed for remaining time)
            remaining_demand = 100 * (remaining_days / 30)  # Normalize to monthly demand
            
            # Check if critical
            if remaining_capacity < remaining_demand * (1 - threshold / 100):
                risk_level = 'RED' if remaining_capacity < remaining_demand * 0.5 else 'AMBER'
                
                critical_projects.append({
                    'project_id': project.id,
                    'project_name': project.project_name,
                    'client_name': project.client_name,
                    'remaining_duration_days': remaining_days,
                    'remaining_allocation_pct': round(remaining_capacity, 2),
                    'remaining_demand_pct': round(remaining_demand, 2),
                    'risk_indicator': risk_level,
                    'team_size': len(allocations)
                })
        
        # Sort by risk level and remaining capacity
        critical_projects.sort(key=lambda x: (x['risk_indicator'] == 'RED', -x['remaining_allocation_pct']))
        
        return jsonify({
            'critical_projects': critical_projects,
            'total_count': len(critical_projects),
            'threshold': threshold
        })
    except Exception as e:
        import traceback
        print(f"Error in get_resource_critical_projects: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/projects/at-risk', methods=['GET'])
def get_projects_at_risk():
    """
    Story 1.2: Identify Projects with Risks or Risky Employees
    Projects marked as at risk due to project-level or employee-level risks
    """
    session = db_tool.Session()
    try:
        today = date.today()
        
        # Get all active projects
        projects = session.query(Project).filter(
            Project.status.in_([ProjectStatus.ACTIVE, ProjectStatus.PIPELINE])
        ).all()
        
        at_risk_projects = []
        
        for project in projects:
            # Check project-level risks
            project_risks = session.query(RiskRegister).filter(
                RiskRegister.project_id == project.id,
                RiskRegister.status != 'CLOSED'
            ).all()
            
            # Get employees on this project
            allocations = session.query(Allocation).filter(
                Allocation.proj_id == project.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            # Check for high-risk employees
            risky_employees = []
            for alloc in allocations:
                employee_risks = session.query(RiskRegister).filter(
                    RiskRegister.emp_id == alloc.emp_id,
                    RiskRegister.severity.in_([RiskSeverity.HIGH, RiskSeverity.CRITICAL]),
                    RiskRegister.status != 'CLOSED'
                ).all()
                if employee_risks:
                    risky_employees.append({
                        'employee_id': alloc.emp_id,
                        'risk_count': len(employee_risks),
                        'risks': [{'type': r.risk_type.value if hasattr(r.risk_type, 'value') else str(r.risk_type), 
                                  'severity': r.severity.value if hasattr(r.severity, 'value') else str(r.severity)} 
                                 for r in employee_risks]
                    })
            
            # Mark as at risk if project has risks OR has risky employees
            if project_risks or risky_employees:
                # Determine overall severity
                all_risks = list(project_risks) + [r for emp in risky_employees for r in emp['risks']]
                max_severity = 'LOW'
                if any(r.get('severity') == 'CRITICAL' for r in all_risks if isinstance(r, dict)):
                    max_severity = 'CRITICAL'
                elif any(r.get('severity') == 'HIGH' for r in all_risks if isinstance(r, dict)):
                    max_severity = 'HIGH'
                elif any(r.severity == RiskSeverity.CRITICAL for r in project_risks):
                    max_severity = 'CRITICAL'
                elif any(r.severity == RiskSeverity.HIGH for r in project_risks):
                    max_severity = 'HIGH'
                
                at_risk_projects.append({
                    'project_id': project.id,
                    'project_name': project.project_name,
                    'client_name': project.client_name,
                    'status': project.status.value if hasattr(project.status, 'value') else str(project.status),
                    'project_risk_count': len(project_risks),
                    'risky_employee_count': len(risky_employees),
                    'severity': max_severity,
                    'project_risks': [{'type': r.risk_type.value if hasattr(r.risk_type, 'value') else str(r.risk_type),
                                      'severity': r.severity.value if hasattr(r.severity, 'value') else str(r.severity)}
                                    for r in project_risks],
                    'risky_employees': risky_employees
                })
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        at_risk_projects.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        return jsonify({
            'at_risk_projects': at_risk_projects,
            'total_count': len(at_risk_projects)
        })
    except Exception as e:
        import traceback
        print(f"Error in get_projects_at_risk: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/projects/low-roi', methods=['GET'])
def get_low_roi_projects():
    """
    Story 1.3: Identify Low-ROI Projects
    Projects generating the lowest ROI (Revenue - Cost)
    """
    session = db_tool.Session()
    try:
        threshold = float(request.args.get('threshold', 10))  # Default 10% ROI threshold
        limit = int(request.args.get('limit', 10))  # Default top 10
        
        # Get active projects
        projects = session.query(Project).filter(
            Project.status == ProjectStatus.ACTIVE
        ).all()
        
        project_rois = []
        
        for project in projects:
            # Get all allocations for this project
            allocations = session.query(Allocation).filter(
                Allocation.proj_id == project.id
            ).all()
            
            total_revenue = 0.0
            total_cost = 0.0
            
            for alloc in allocations:
                if alloc.financials:
                    total_revenue += alloc.financials.actual_revenue or 0.0
                    total_cost += alloc.financials.actual_cost or 0.0
                else:
                    # Calculate from allocation if financials not available
                    if alloc.billing_rate:
                        # Simplified calculation
                        hours = 160  # Monthly hours
                        allocation_pct = get_internal_allocation_percentage(alloc)
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        total_revenue += alloc.billing_rate * billed_hours
                    
                    if alloc.employee:
                        cost_rate = calculate_hourly_cost(alloc.employee)
                        internal_pct = get_internal_allocation_percentage(alloc)
                        cost_hours = 160 * (internal_pct / 100)
                        total_cost += cost_rate * cost_hours
            
            # Calculate ROI
            profit = total_revenue - total_cost
            roi_percentage = (profit / total_cost * 100) if total_cost > 0 else 0
            
            project_rois.append({
                'project_id': project.id,
                'project_name': project.project_name,
                'client_name': project.client_name,
                'revenue': round(total_revenue, 2),
                'cost': round(total_cost, 2),
                'profit': round(profit, 2),
                'roi_percentage': round(roi_percentage, 2),
                'is_below_threshold': roi_percentage < threshold
            })
        
        # Sort by ROI (lowest first)
        project_rois.sort(key=lambda x: x['roi_percentage'])
        
        # Return bottom performers
        low_roi = [p for p in project_rois if p['is_below_threshold']][:limit]
        
        return jsonify({
            'low_roi_projects': low_roi,
            'total_count': len(low_roi),
            'threshold': threshold
        })
    except Exception as e:
        import traceback
        print(f"Error in get_low_roi_projects: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/projects/high-roi', methods=['GET'])
def get_high_roi_projects():
    """
    Story 1.4: Identify High-ROI / Star Projects
    Three reports: Highest ROI, Most Efficient, Most Stable High-Performing
    """
    session = db_tool.Session()
    try:
        report_type = request.args.get('type', 'highest_roi')  # highest_roi, most_efficient, most_stable
        limit = int(request.args.get('limit', 10))
        
        projects = session.query(Project).filter(
            Project.status == ProjectStatus.ACTIVE
        ).all()
        
        project_data = []
        today = date.today()
        
        for project in projects:
            allocations = session.query(Allocation).filter(
                Allocation.proj_id == project.id
            ).all()
            
            total_revenue = 0.0
            total_cost = 0.0
            total_internal_allocation = 0
            team_size = len(allocations)
            
            # Check for risks
            project_risks = session.query(RiskRegister).filter(
                RiskRegister.project_id == project.id,
                RiskRegister.status != 'CLOSED'
            ).count()
            
            for alloc in allocations:
                internal_pct = get_internal_allocation_percentage(alloc)
                total_internal_allocation += internal_pct
                
                if alloc.financials:
                    total_revenue += alloc.financials.actual_revenue or 0.0
                    total_cost += alloc.financials.actual_cost or 0.0
                else:
                    if alloc.billing_rate:
                        hours = 160
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        allocation_pct = getattr(alloc, 'allocation_percentage', internal_pct) or internal_pct
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        total_revenue += alloc.billing_rate * billed_hours
                    
                    if alloc.employee:
                        cost_rate = calculate_hourly_cost(alloc.employee)
                        cost_hours = 160 * (internal_pct / 100)
                        total_cost += cost_rate * cost_hours
            
            profit = total_revenue - total_cost
            roi_percentage = (profit / total_cost * 100) if total_cost > 0 else 0
            efficiency = (profit / total_internal_allocation) if total_internal_allocation > 0 else 0
            
            project_data.append({
                'project_id': project.id,
                'project_name': project.project_name,
                'client_name': project.client_name,
                'revenue': round(total_revenue, 2),
                'cost': round(total_cost, 2),
                'profit': round(profit, 2),
                'roi_percentage': round(roi_percentage, 2),
                'efficiency': round(efficiency, 2),
                'team_size': team_size,
                'risk_count': project_risks,
                'total_allocation': total_internal_allocation,
                'is_stable': project_risks == 0 and team_size > 0
            })
        
        # Sort based on report type
        if report_type == 'highest_roi':
            project_data.sort(key=lambda x: x['roi_percentage'], reverse=True)
        elif report_type == 'most_efficient':
            project_data.sort(key=lambda x: x['efficiency'], reverse=True)
        elif report_type == 'most_stable':
            # High ROI + low risk + stable utilization
            project_data.sort(key=lambda x: (
                x['is_stable'],
                x['roi_percentage'],
                -x['risk_count']
            ), reverse=True)
        
        # Tag star performers (top performers with high ROI)
        star_threshold = 30  # 30% ROI
        for p in project_data[:limit]:
            if p['roi_percentage'] >= star_threshold and p['risk_count'] == 0:
                p['is_star_performer'] = True
            else:
                p['is_star_performer'] = False
        
        return jsonify({
            'report_type': report_type,
            'high_roi_projects': project_data[:limit],
            'total_count': len(project_data)
        })
    except Exception as e:
        import traceback
        print(f"Error in get_high_roi_projects: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ============================================================================
# EPIC 2: Employee Intelligence & Workforce Optimization
# ============================================================================

@bp.route('/employees/at-risk', methods=['GET'])
def get_employees_at_risk():
    """
    Story 2.1: Identify Employees at Risk or Under-Utilized
    Employees marked as at risk, resigning, or under-allocated (<25%)
    """
    session = db_tool.Session()
    try:
        today = date.today()
        underutilization_threshold = float(request.args.get('threshold', 25))
        
        # Get all employees
        employees = session.query(Employee).all()
        
        at_risk_employees = []
        
        for employee in employees:
            # Check employee status
            is_resigning = employee.status == EmployeeStatus.NOTICE_PERIOD
            
            # Get active allocations
            allocations = session.query(Allocation).filter(
                Allocation.emp_id == employee.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            # Calculate total internal allocation
            total_internal_allocation = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            
            # Check for risks
            risks = session.query(RiskRegister).filter(
                RiskRegister.emp_id == employee.id,
                RiskRegister.status != 'CLOSED'
            ).all()
            
            # Determine if at risk
            risk_reasons = []
            if is_resigning:
                risk_reasons.append('NOTICE_PERIOD')
            if total_internal_allocation < underutilization_threshold:
                risk_reasons.append('UNDER_UTILIZED')
            if risks:
                risk_reasons.append('HAS_RISKS')
            
            if risk_reasons:
                at_risk_employees.append({
                    'employee_id': employee.id,
                    'employee_name': f"{employee.first_name} {employee.last_name}",
                    'email': employee.email,
                    'status': get_derived_employee_status(employee, session).value,
                    'internal_allocation_percentage': round(total_internal_allocation, 2),
                    'risk_reasons': risk_reasons,
                    'risk_count': len(risks),
                    'risks': [{'type': r.risk_type.value if hasattr(r.risk_type, 'value') else str(r.risk_type),
                             'severity': r.severity.value if hasattr(r.severity, 'value') else str(r.severity)}
                            for r in risks]
                })
        
        # Sort by risk severity
        at_risk_employees.sort(key=lambda x: (
            'NOTICE_PERIOD' in x['risk_reasons'],
            -x['risk_count'],
            x['internal_allocation_percentage']
        ), reverse=True)
        
        return jsonify({
            'at_risk_employees': at_risk_employees,
            'total_count': len(at_risk_employees),
            'threshold': underutilization_threshold
        })
    except Exception as e:
        import traceback
        print(f"Error in get_employees_at_risk: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/employees/hiring-needs', methods=['GET'])
def get_hiring_needs():
    """
    Story 2.2: Identify Hiring Needs for Pipeline Projects
    Skills required for upcoming projects that are unavailable internally
    """
    session = db_tool.Session()
    try:
        today = date.today()
        
        # Get pipeline projects
        pipeline_projects = session.query(Project).filter(
            Project.status == ProjectStatus.PIPELINE
        ).all()
        
        # Get all employee skills
        employee_skills = {}
        employees = session.query(Employee).all()
        for emp in employees:
            for skill in emp.skills:
                skill_name = skill.skill_name.lower()
                if skill_name not in employee_skills:
                    employee_skills[skill_name] = []
                employee_skills[skill_name].append({
                    'employee_id': emp.id,
                    'proficiency': skill.proficiency
                })
        
        # Analyze pipeline project requirements
        hiring_needs = {}
        
        for project in pipeline_projects:
            # Get role requirements
            role_requirements = session.query(ProjectRoleRequirements).filter(
                ProjectRoleRequirements.proj_id == project.id
            ).all()
            
            for req in role_requirements:
                # For now, we'll need to infer skills from role name or use a skill mapping
                # This is simplified - in production, you'd have a proper skill-role mapping
                role_name = req.role_name.lower()
                required_count = req.required_count or 1
                
                # Check if we have employees with matching skills
                # This is a simplified check - in production, use proper skill matching
                available_count = 0
                for skill_name, emp_list in employee_skills.items():
                    if role_name in skill_name or skill_name in role_name:
                        available_count += len([e for e in emp_list if e['proficiency'] >= 3])
                
                if available_count < required_count:
                    key = f"{role_name}_{project.id}"
                    if key not in hiring_needs:
                        hiring_needs[key] = {
                            'skill': role_name,
                            'project_id': project.id,
                            'project_name': project.project_name,
                            'required_count': required_count,
                            'available_count': available_count,
                            'needed_count': required_count - available_count
                        }
        
        needs_list = list(hiring_needs.values())
        needs_list.sort(key=lambda x: x['needed_count'], reverse=True)
        
        return jsonify({
            'hiring_needs': needs_list,
            'total_count': len(needs_list)
        })
    except Exception as e:
        import traceback
        print(f"Error in get_hiring_needs: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/employees/upskilling-opportunities', methods=['GET'])
def get_upskilling_opportunities():
    """
    Story 2.3: Identify Employees Suitable for Upskilling
    Employees who can be trained to meet upcoming project needs
    """
    session = db_tool.Session()
    try:
        today = date.today()
        
        # Get pipeline projects and their requirements
        pipeline_projects = session.query(Project).filter(
            Project.status == ProjectStatus.PIPELINE
        ).all()
        
        # Get under-utilized employees (<50% allocation)
        employees = session.query(Employee).all()
        upskilling_opportunities = []
        
        for employee in employees:
            # Get current allocations
            allocations = session.query(Allocation).filter(
                Allocation.emp_id == employee.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            total_allocation = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            
            # Only consider under-utilized employees
            if total_allocation < 50:
                # Get employee's current skills
                current_skills = {s.skill_name.lower(): s.proficiency for s in employee.skills}
                
                # Find matching pipeline projects
                for project in pipeline_projects:
                    role_requirements = session.query(ProjectRoleRequirements).filter(
                        ProjectRoleRequirements.proj_id == project.id
                    ).all()
                    
                    for req in role_requirements:
                        role_name = req.role_name.lower()
                        # Check if employee has adjacent skills
                        # Simplified: check if any current skill is related
                        has_adjacent_skill = any(
                            role_name in skill or skill in role_name
                            for skill in current_skills.keys()
                        )
                        
                        if has_adjacent_skill:
                            upskilling_opportunities.append({
                                'employee_id': employee.id,
                                'employee_name': f"{employee.first_name} {employee.last_name}",
                                'current_allocation_pct': round(total_allocation, 2),
                                'current_skills': list(current_skills.keys()),
                                'target_skill': role_name,
                                'project_id': project.id,
                                'project_name': project.project_name,
                                'estimated_training_effort': 'MEDIUM',  # Simplified
                                'is_trainable': True
                            })
                            break  # One opportunity per employee
        
        return jsonify({
            'upskilling_opportunities': upskilling_opportunities,
            'total_count': len(upskilling_opportunities)
        })
    except Exception as e:
        import traceback
        print(f"Error in get_upskilling_opportunities: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/employees/low-roi', methods=['GET'])
def get_low_roi_employees():
    """
    Story 2.4: Identify Low-ROI Employees Based on Profit-to-Allocation Ratio
    Employees generating low profit relative to their internal allocation percentage
    """
    session = db_tool.Session()
    try:
        today = date.today()
        threshold = float(request.args.get('threshold', 50))  # Default profit efficiency threshold
        limit = int(request.args.get('limit', 20))
        
        employees = session.query(Employee).all()
        employee_rois = []
        
        for employee in employees:
            # Get active allocations
            allocations = session.query(Allocation).filter(
                Allocation.emp_id == employee.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            if not allocations:
                continue
            
            # Calculate total internal allocation
            total_internal_allocation = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            
            # Calculate total profit
            total_revenue = 0.0
            total_cost = 0.0
            project_breakdown = []
            
            for alloc in allocations:
                project_revenue = 0.0
                project_cost = 0.0
                
                if alloc.financials:
                    project_revenue = alloc.financials.actual_revenue or 0.0
                    project_cost = alloc.financials.actual_cost or 0.0
                else:
                    # Calculate from allocation
                    if alloc.billing_rate:
                        hours = 160
                        allocation_pct = getattr(alloc, 'allocation_percentage', get_internal_allocation_percentage(alloc)) or get_internal_allocation_percentage(alloc)
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        project_revenue = alloc.billing_rate * billed_hours
                    
                    cost_rate = calculate_hourly_cost(employee)
                    internal_pct = get_internal_allocation_percentage(alloc)
                    cost_hours = 160 * (internal_pct / 100)
                    project_cost = cost_rate * cost_hours
                
                total_revenue += project_revenue
                total_cost += project_cost
                
                project_breakdown.append({
                    'project_id': alloc.proj_id,
                    'project_name': alloc.project.project_name if alloc.project else 'Unknown',
                    'allocation_pct': get_internal_allocation_percentage(alloc),
                    'revenue': round(project_revenue, 2),
                    'cost': round(project_cost, 2),
                    'profit': round(project_revenue - project_cost, 2)
                })
            
            total_profit = total_revenue - total_cost
            
            # Calculate profit-to-allocation efficiency
            if total_internal_allocation > 0:
                profit_efficiency = (total_profit / total_internal_allocation) * 100
            else:
                profit_efficiency = 0
            
            # Flag if low ROI
            is_low_roi = profit_efficiency < threshold or (total_internal_allocation > 70 and total_profit < 0)
            
            employee_rois.append({
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'email': employee.email,
                'internal_allocation_percentage': round(total_internal_allocation, 2),
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'total_profit': round(total_profit, 2),
                'profit_to_allocation_ratio': round(profit_efficiency, 2),
                'is_low_roi': is_low_roi,
                'projects': project_breakdown
            })
        
        # Sort by profit efficiency (lowest first)
        employee_rois.sort(key=lambda x: x['profit_to_allocation_ratio'])
        
        # Return bottom performers
        low_roi = [e for e in employee_rois if e['is_low_roi']][:limit]
        
        return jsonify({
            'low_roi_employees': low_roi,
            'total_count': len(low_roi),
            'threshold': threshold
        })
    except Exception as e:
        import traceback
        print(f"Error in get_low_roi_employees: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/employees/star-performers', methods=['GET'])
def get_star_employees():
    """
    Story 2.5: Identify Star Employees Using Allocation-Adjusted Performance
    Three reports: Highest Profit-to-Allocation, Best Utilization, Consistently High Performers
    """
    session = db_tool.Session()
    try:
        report_type = request.args.get('type', 'highest_ratio')  # highest_ratio, best_utilization, consistent
        limit = int(request.args.get('limit', 20))
        today = date.today()
        
        employees = session.query(Employee).all()
        employee_data = []
        
        for employee in employees:
            allocations = session.query(Allocation).filter(
                Allocation.emp_id == employee.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            if not allocations:
                continue
            
            total_internal_allocation = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            total_revenue = 0.0
            total_cost = 0.0
            project_contributions = []
            
            # Check for risks
            risks = session.query(RiskRegister).filter(
                RiskRegister.emp_id == employee.id,
                RiskRegister.status != 'CLOSED'
            ).count()
            
            for alloc in allocations:
                project_revenue = 0.0
                project_cost = 0.0
                
                if alloc.financials:
                    project_revenue = alloc.financials.actual_revenue or 0.0
                    project_cost = alloc.financials.actual_cost or 0.0
                else:
                    if alloc.billing_rate:
                        hours = 160
                        allocation_pct = getattr(alloc, 'allocation_percentage', get_internal_allocation_percentage(alloc)) or get_internal_allocation_percentage(alloc)
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        project_revenue = alloc.billing_rate * billed_hours
                    
                    cost_rate = calculate_hourly_cost(employee)
                    internal_pct = get_internal_allocation_percentage(alloc)
                    cost_hours = 160 * (internal_pct / 100)
                    project_cost = cost_rate * cost_hours
                
                total_revenue += project_revenue
                total_cost += project_cost
                
                project_contributions.append({
                    'project_id': alloc.proj_id,
                    'project_name': alloc.project.project_name if alloc.project else 'Unknown',
                    'allocation_pct': get_internal_allocation_percentage(alloc),
                    'profit': round(project_revenue - project_cost, 2)
                })
            
            total_profit = total_revenue - total_cost
            
            # Calculate metrics
            if total_internal_allocation > 0:
                profit_to_allocation_ratio = (total_profit / total_internal_allocation) * 100
            else:
                profit_to_allocation_ratio = 0
            
            employee_data.append({
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'email': employee.email,
                'internal_allocation_percentage': round(total_internal_allocation, 2),
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'total_profit': round(total_profit, 2),
                'profit_to_allocation_ratio': round(profit_to_allocation_ratio, 2),
                'risk_count': risks,
                'project_count': len(allocations),
                'project_contributions': project_contributions,
                'is_high_utilization': total_internal_allocation >= 80,
                'is_balanced': 60 <= total_internal_allocation <= 90,
                'is_low_risk': risks == 0
            })
        
        # Sort based on report type
        if report_type == 'highest_ratio':
            employee_data.sort(key=lambda x: x['profit_to_allocation_ratio'], reverse=True)
        elif report_type == 'best_utilization':
            # High allocation (>80%) with high profit
            employee_data.sort(key=lambda x: (
                x['is_high_utilization'],
                x['total_profit']
            ), reverse=True)
        elif report_type == 'consistent':
            # Balanced allocation (60-90%) with strong ROI and low risk
            employee_data.sort(key=lambda x: (
                x['is_balanced'],
                x['is_low_risk'],
                x['profit_to_allocation_ratio']
            ), reverse=True)
        
        # Tag star performers
        for emp in employee_data[:limit]:
            if (emp['profit_to_allocation_ratio'] > 100 and 
                emp['is_low_risk'] and 
                emp['total_profit'] > 0):
                emp['is_star_performer'] = True
            else:
                emp['is_star_performer'] = False
        
        return jsonify({
            'report_type': report_type,
            'star_employees': employee_data[:limit],
            'total_count': len(employee_data)
        })
    except Exception as e:
        import traceback
        print(f"Error in get_star_employees: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/employees/profit-efficiency', methods=['GET'])
def get_employee_profit_efficiency():
    """
    Story 2.6: Analyze Employee Profit Efficiency in Project Context
    How efficiently employees generate profit relative to allocation across projects
    """
    session = db_tool.Session()
    try:
        today = date.today()
        employee_id = request.args.get('employee_id', type=int)
        
        query = session.query(Employee)
        if employee_id:
            query = query.filter(Employee.id == employee_id)
        
        employees = query.all()
        efficiency_data = []
        
        for employee in employees:
            allocations = session.query(Allocation).filter(
                Allocation.emp_id == employee.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            if not allocations:
                continue
            
            total_internal_allocation = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            total_profit = 0.0
            project_breakdown = []
            
            for alloc in allocations:
                project_revenue = 0.0
                project_cost = 0.0
                
                if alloc.financials:
                    project_revenue = alloc.financials.actual_revenue or 0.0
                    project_cost = alloc.financials.actual_cost or 0.0
                else:
                    if alloc.billing_rate:
                        hours = 160
                        allocation_pct = getattr(alloc, 'allocation_percentage', get_internal_allocation_percentage(alloc)) or get_internal_allocation_percentage(alloc)
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        project_revenue = alloc.billing_rate * billed_hours
                    
                    cost_rate = calculate_hourly_cost(employee)
                    internal_pct = get_internal_allocation_percentage(alloc)
                    cost_hours = 160 * (internal_pct / 100)
                    project_cost = cost_rate * cost_hours
                
                project_profit = project_revenue - project_cost
                total_profit += project_profit
                
                project_breakdown.append({
                    'project_id': alloc.proj_id,
                    'project_name': alloc.project.project_name if alloc.project else 'Unknown',
                    'allocation_pct': get_internal_allocation_percentage(alloc),
                    'revenue': round(project_revenue, 2),
                    'cost': round(project_cost, 2),
                    'profit': round(project_profit, 2),
                    'profit_per_allocation': round(project_profit / get_internal_allocation_percentage(alloc), 2) if get_internal_allocation_percentage(alloc) > 0 else 0
                })
            
            # Calculate overall efficiency
            if total_internal_allocation > 0:
                efficiency_score = (total_profit / total_internal_allocation) * 100
            else:
                efficiency_score = 0
            
            # Determine efficiency level
            if efficiency_score >= 100:
                efficiency_level = 'GREEN'
            elif efficiency_score >= 50:
                efficiency_level = 'AMBER'
            else:
                efficiency_level = 'RED'
            
            efficiency_data.append({
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'total_internal_allocation_pct': round(total_internal_allocation, 2),
                'total_profit': round(total_profit, 2),
                'profit_to_allocation_ratio': round(efficiency_score, 2),
                'efficiency_level': efficiency_level,
                'project_breakdown': project_breakdown,
                'recommendations': _generate_reallocation_recommendations(project_breakdown)
            })
        
        # Sort by efficiency score
        efficiency_data.sort(key=lambda x: x['profit_to_allocation_ratio'], reverse=True)
        
        return jsonify({
            'efficiency_data': efficiency_data,
            'total_count': len(efficiency_data)
        })
    except Exception as e:
        import traceback
        print(f"Error in get_employee_profit_efficiency: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


def _generate_reallocation_recommendations(project_breakdown):
    """Generate reallocation recommendations based on project profit efficiency"""
    recommendations = []
    
    # Find high allocation on low-profit projects
    for project in project_breakdown:
        if project['allocation_pct'] > 50 and project['profit_per_allocation'] < 0:
            recommendations.append({
                'type': 'REALLOCATE',
                'message': f"High allocation ({project['allocation_pct']}%) on low-profit project: {project['project_name']}",
                'project_id': project['project_id']
            })
    
    # Find under-allocation on high-profit projects
    high_profit_projects = [p for p in project_breakdown if p['profit_per_allocation'] > 100]
    low_allocation_high_profit = [p for p in high_profit_projects if p['allocation_pct'] < 30]
    
    if low_allocation_high_profit:
        recommendations.append({
            'type': 'INCREASE_ALLOCATION',
            'message': f"Consider increasing allocation on high-profit projects",
            'projects': [p['project_id'] for p in low_allocation_high_profit]
        })
    
    return recommendations


# ============================================================================
# EPIC 3: Risk & Financial Performance Management
# ============================================================================

@bp.route('/risks/consolidated', methods=['GET'])
def get_consolidated_risks():
    """
    Story 3.1: Consolidated Project & Employee Risk View
    Single view of all project and employee risks
    """
    session = db_tool.Session()
    try:
        today = date.today()
        
        # Get all active risks
        risks = session.query(RiskRegister).filter(
            RiskRegister.status != 'CLOSED'
        ).all()
        
        project_risks = []
        employee_risks = []
        
        for risk in risks:
            risk_data = {
                'risk_id': risk.id,
                'risk_type': risk.risk_type.value if hasattr(risk.risk_type, 'value') else str(risk.risk_type),
                'severity': risk.severity.value if hasattr(risk.severity, 'value') else str(risk.severity),
                'status': risk.status.value if hasattr(risk.status, 'value') else str(risk.status),
                'description': risk.description,
                'mitigation_plan': risk.mitigation_plan,
                'identified_date': risk.identified_date.isoformat() if risk.identified_date else None,
                'target_resolution_date': risk.target_resolution_date.isoformat() if risk.target_resolution_date else None
            }
            
            if risk.project_id:
                project = session.query(Project).get(risk.project_id)
                risk_data['project_id'] = risk.project_id
                risk_data['project_name'] = project.project_name if project else 'Unknown'
                risk_data['client_name'] = project.client_name if project else None
                project_risks.append(risk_data)
            
            if risk.emp_id:
                employee = session.query(Employee).get(risk.emp_id)
                risk_data['employee_id'] = risk.emp_id
                risk_data['employee_name'] = f"{employee.first_name} {employee.last_name}" if employee else 'Unknown'
                employee_risks.append(risk_data)
        
        # Group by category
        risk_by_category = {}
        risk_by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        
        all_risks = project_risks + employee_risks
        for risk in all_risks:
            risk_type = risk['risk_type']
            if risk_type not in risk_by_category:
                risk_by_category[risk_type] = []
            risk_by_category[risk_type].append(risk)
            
            severity = risk['severity']
            if severity in risk_by_severity:
                risk_by_severity[severity].append(risk)
        
        return jsonify({
            'project_risks': project_risks,
            'employee_risks': employee_risks,
            'risks_by_category': risk_by_category,
            'risks_by_severity': risk_by_severity,
            'total_count': len(all_risks),
            'summary': {
                'critical': len(risk_by_severity['CRITICAL']),
                'high': len(risk_by_severity['HIGH']),
                'medium': len(risk_by_severity['MEDIUM']),
                'low': len(risk_by_severity['LOW'])
            }
        })
    except Exception as e:
        import traceback
        print(f"Error in get_consolidated_risks: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/projects/financially-underperforming', methods=['GET'])
def get_financially_underperforming_projects():
    """
    Story 3.2: Identify Financially Underperforming Projects
    Projects with margin below threshold
    """
    session = db_tool.Session()
    try:
        margin_threshold = float(request.args.get('threshold', 20))  # Default 20% margin
        
        projects = session.query(Project).filter(
            Project.status == ProjectStatus.ACTIVE
        ).all()
        
        underperforming = []
        
        for project in projects:
            allocations = session.query(Allocation).filter(
                Allocation.proj_id == project.id
            ).all()
            
            total_revenue = 0.0
            total_cost = 0.0
            
            for alloc in allocations:
                if alloc.financials:
                    total_revenue += alloc.financials.actual_revenue or 0.0
                    total_cost += alloc.financials.actual_cost or 0.0
                else:
                    if alloc.billing_rate:
                        hours = 160
                        allocation_pct = getattr(alloc, 'allocation_percentage', get_internal_allocation_percentage(alloc)) or get_internal_allocation_percentage(alloc)
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        total_revenue += alloc.billing_rate * billed_hours
                    
                    if alloc.employee:
                        cost_rate = calculate_hourly_cost(alloc.employee)
                        internal_pct = get_internal_allocation_percentage(alloc)
                        cost_hours = 160 * (internal_pct / 100)
                        total_cost += cost_rate * cost_hours
            
            # Calculate margin
            if total_revenue > 0:
                margin = ((total_revenue - total_cost) / total_revenue) * 100
            else:
                margin = 0
            
            if margin < margin_threshold:
                underperforming.append({
                    'project_id': project.id,
                    'project_name': project.project_name,
                    'client_name': project.client_name,
                    'revenue': round(total_revenue, 2),
                    'cost': round(total_cost, 2),
                    'margin_percentage': round(margin, 2),
                    'is_below_threshold': True,
                    'budget_cap': project.budget_cap,
                    'budget_consumed': round(total_cost, 2)
                })
        
        # Sort by margin (lowest first)
        underperforming.sort(key=lambda x: x['margin_percentage'])
        
        return jsonify({
            'underperforming_projects': underperforming,
            'total_count': len(underperforming),
            'threshold': margin_threshold
        })
    except Exception as e:
        import traceback
        print(f"Error in get_financially_underperforming_projects: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@bp.route('/employees/low-gross-profit', methods=['GET'])
def get_low_gross_profit_employees():
    """
    Story 3.3: Identify Employees with Low Gross Profit Contribution Relative to Allocation
    Employees not contributing enough to gross profit relative to internal allocation percentage
    """
    session = db_tool.Session()
    try:
        today = date.today()
        threshold = float(request.args.get('threshold', 50))  # Default threshold
        
        employees = session.query(Employee).all()
        low_performers = []
        
        for employee in employees:
            allocations = session.query(Allocation).filter(
                Allocation.emp_id == employee.id,
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= today
                )
            ).all()
            
            if not allocations:
                continue
            
            total_internal_allocation = sum(get_internal_allocation_percentage(alloc) for alloc in allocations)
            total_gross_profit = 0.0
            project_contributions = []
            
            for alloc in allocations:
                revenue = 0.0
                cost = 0.0
                
                if alloc.financials:
                    revenue = alloc.financials.actual_revenue or 0.0
                    cost = alloc.financials.actual_cost or 0.0
                else:
                    if alloc.billing_rate:
                        hours = 160
                        allocation_pct = getattr(alloc, 'allocation_percentage', get_internal_allocation_percentage(alloc)) or get_internal_allocation_percentage(alloc)
                        billable_pct = getattr(alloc, 'billable_percentage', 100) or 100
                        billed_hours = hours * (allocation_pct / 100) * (billable_pct / 100)
                        revenue = alloc.billing_rate * billed_hours
                    
                    cost_rate = calculate_hourly_cost(employee)
                    internal_pct = get_internal_allocation_percentage(alloc)
                    cost_hours = 160 * (internal_pct / 100)
                    cost = cost_rate * cost_hours
                
                gross_profit = revenue - cost
                total_gross_profit += gross_profit
                
                project_contributions.append({
                    'project_id': alloc.proj_id,
                    'project_name': alloc.project.project_name if alloc.project else 'Unknown',
                    'allocation_pct': get_internal_allocation_percentage(alloc),
                    'gross_profit': round(gross_profit, 2)
                })
            
            # Calculate allocation-adjusted gross profit
            if total_internal_allocation > 0:
                allocation_adjusted_gp = (total_gross_profit / total_internal_allocation) * 100
            else:
                allocation_adjusted_gp = 0
            
            # Flag if below threshold
            if allocation_adjusted_gp < threshold:
                low_performers.append({
                    'employee_id': employee.id,
                    'employee_name': f"{employee.first_name} {employee.last_name}",
                    'email': employee.email,
                    'internal_allocation_percentage': round(total_internal_allocation, 2),
                    'gross_profit': round(total_gross_profit, 2),
                    'allocation_adjusted_gross_profit': round(allocation_adjusted_gp, 2),
                    'is_below_threshold': True,
                    'project_contributions': project_contributions
                })
        
        # Sort by allocation-adjusted gross profit (lowest first)
        low_performers.sort(key=lambda x: x['allocation_adjusted_gross_profit'])
        
        return jsonify({
            'low_gross_profit_employees': low_performers,
            'total_count': len(low_performers),
            'threshold': threshold
        })
    except Exception as e:
        import traceback
        print(f"Error in get_low_gross_profit_employees: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
