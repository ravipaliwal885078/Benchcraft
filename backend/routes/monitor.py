"""
Continuous Monitoring and Feedback Route
Returns utilization, bench burn, and feedback summary (stub)
"""
from flask import Blueprint, jsonify

bp = Blueprint('monitor', __name__)

@bp.route('/dashboard', methods=['GET'])
def dashboard_metrics():
    # In production, aggregate real metrics from DB
    # Stubbed response
    metrics = {
        'bench_burn_cost': 12000,
        'avg_time_to_allocation': 8,
        'utilization_rate': 0.87,
        'training_roi': 2.1,
        'attrition_rate': 0.09,
        'feedback_summary': {
            'positive': 78,
            'neutral': 15,
            'negative': 7
        }
    }
    return jsonify(metrics)
