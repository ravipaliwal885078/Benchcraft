"""
HR Verification and Profile Activation Routes
"""
from flask import Blueprint, request, jsonify
from tools.sql_db import SQLDatabaseTool
from models import Employee, EmployeeStatus

bp = Blueprint('hr', __name__)
db_tool = SQLDatabaseTool()

@bp.route('/pending', methods=['GET'])
def get_pending_profiles():
    session = db_tool.Session()
    employees = session.query(Employee).filter(Employee.status == EmployeeStatus.BENCH).all()
    result = [
        {
            'id': emp.id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'email': emp.email,
            'status': emp.status.value
        }
        for emp in employees
    ]
    return jsonify(result)

@bp.route('/verify/<int:emp_id>', methods=['POST'])
def verify_profile(emp_id):
    session = db_tool.Session()
    emp = session.query(Employee).get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    emp.status = EmployeeStatus.ALLOCATED
    session.commit()
    return jsonify({'message': 'Profile verified and activated', 'id': emp.id})
