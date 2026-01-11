"""
Dashboard Routes
/kpi - Key performance indicators
"""
from flask import Blueprint, jsonify
from tools.sql_db import SQLDatabaseTool

bp = Blueprint('dashboard', __name__)
db_tool = SQLDatabaseTool()

@bp.route('/kpi', methods=['GET'])
def get_kpi():
    """Get dashboard KPIs including bench burn"""
    bench_data = db_tool.calculate_bench_burn()
    
    # Get total employees
    from models import Employee, Allocation, Project, EmployeeStatus, ProjectStatus
    session = db_tool.Session()
    try:
        total_employees = session.query(Employee).count()
        allocated_employees = session.query(Employee).filter(
            Employee.status == EmployeeStatus.ALLOCATED
        ).count()
        
        active_projects = session.query(Project).filter(
            Project.status == ProjectStatus.ACTIVE
        ).count()
        
        return jsonify({
            'bench_burn': {
                'bench_count': bench_data['bench_count'],
                'total_monthly_cost': bench_data['total_monthly_cost'],
                'currency': 'USD'  # Default, should be calculated from employees
            },
            'utilization': {
                'total_employees': total_employees,
                'allocated': allocated_employees,
                'on_bench': bench_data['bench_count'],
                'utilization_rate': (allocated_employees / total_employees * 100) if total_employees > 0 else 0
            },
            'projects': {
                'active': active_projects
            }
        })
    finally:
        session.close()

@bp.route('/forecast', methods=['GET'])
def get_forecast():
    """Get revenue forecast data"""
    from datetime import datetime, timedelta
    import random
    
    # Generate realistic forecast data based on current allocations
    session = db_tool.Session()
    try:
        # Get current allocation billing rates
        from models import Allocation
        current_allocations = session.query(Allocation).filter(
            Allocation.end_date.is_(None) | (Allocation.end_date >= datetime.now().date())
        ).all()
        
        total_monthly_revenue = sum(alloc.billing_rate * 160 for alloc in current_allocations if alloc.billing_rate)  # Assuming 160 hours/month
        
        # Generate 6 months of forecast data with some growth
        forecast_data = []
        base_revenue = total_monthly_revenue
        base_savings = total_monthly_revenue * 0.25  # Assume 25% cost savings from optimization
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        for i, month in enumerate(months):
            growth_factor = 1 + (i * 0.05)  # 5% monthly growth
            revenue = int(base_revenue * growth_factor)
            saved = int(base_savings * growth_factor)
            
            forecast_data.append({
                'month': month,
                'revenue': revenue,
                'saved': saved
            })
        
        return jsonify({
            'forecast': forecast_data
        })
    finally:
        session.close()
