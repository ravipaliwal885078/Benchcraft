"""
Project Management Routes
/projects - CRUD for projects
"""
from flask import Blueprint, request, jsonify
from tools.sql_db import SQLDatabaseTool
from tools.vector_db import ChromaSearchTool
from models import Project, ProjectStatus
from datetime import datetime

bp = Blueprint('projects', __name__)
db_tool = SQLDatabaseTool()
vector_tool = ChromaSearchTool()

@bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    projects = db_tool.get_all_projects()
    return jsonify({
        'projects': [
            {
                'id': p.id,
                'client_name': p.client_name,
                'project_name': p.project_name,
                'description': p.description,
                'budget_cap': p.budget_cap,
                'start_date': p.start_date.isoformat() if p.start_date else None,
                'end_date': p.end_date.isoformat() if p.end_date else None,
                'status': p.status.value if p.status else None,
                'probability': p.probability,
                'tech_stack': p.tech_stack
            }
            for p in projects
        ]
    })

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
        allocations = [{
            'id': alloc.id,
            'employee_id': alloc.employee.id,
            'employee_uuid': alloc.employee.uuid,
            'first_name': alloc.employee.first_name,
            'last_name': alloc.employee.last_name,
            'role_level': alloc.employee.role_level.value if alloc.employee.role_level else None,
            'start_date': alloc.start_date.isoformat(),
            'end_date': alloc.end_date.isoformat() if alloc.end_date else None,
            'billing_rate': alloc.billing_rate,
            'utilization': alloc.utilization,
            'is_revealed': alloc.is_revealed
        } for alloc in project.allocations]

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
        total_budget_used = sum(a['billing_rate'] or 0 for a in allocations if a['billing_rate'])
        avg_utilization = sum(a['utilization'] or 100 for a in allocations) / len(allocations) if allocations else 0

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
                'budget_utilized': total_budget_used,
                'budget_remaining': project.budget_cap - total_budget_used,
                'avg_utilization': round(avg_utilization, 1),
                'total_allocations': len(allocations)
            }
        })
    finally:
        session.close()
