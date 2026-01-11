"""
Risk and Notice Period Management Route
Returns notice period status and risk assessment (stub)
"""
from flask import Blueprint, request, jsonify

bp = Blueprint('risk', __name__)

@bp.route('/notice-status', methods=['POST'])
def notice_status():
    data = request.json
    # In production, fetch from DB and calculate risk
    # Stubbed response
    status = {
        'employee': data.get('employee', 'John Doe'),
        'notice_period': True,
        'days_remaining': 45,
        'risk_level': 'HIGH',
        'project_impact': 'Critical resource, replacement needed',
        'kt_status': 'In Progress'
    }
    return jsonify(status)
