"""
Training and Skill Gap Analysis Route
Upskilling recommendations over hiring
"""
from flask import Blueprint, request, jsonify
from agents.training_recommendation_agent import TrainingRecommendationAgent

bp = Blueprint('training', __name__)

# Initialize agent (singleton pattern)
_training_agent = None

def get_training_agent():
    """Get or create training recommendation agent"""
    global _training_agent
    if _training_agent is None:
        _training_agent = TrainingRecommendationAgent()
    return _training_agent

@bp.route('/recommendations', methods=['GET'])
def get_training_recommendations():
    """
    Get AI-powered training recommendations for upcoming projects
    Analyzes skill gaps and recommends upskilling over hiring
    """
    try:
        agent = get_training_agent()
        result = agent.analyze_skill_gaps_and_recommend_training()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate training recommendations'
        }), 500

@bp.route('/gap-analysis', methods=['POST'])
def skill_gap_analysis():
    """
    Legacy endpoint - kept for backward compatibility
    For employee-specific skill gap analysis
    """
    data = request.json or {}
    emp_id = data.get('employee_id')
    project_id = data.get('project_id')
    
    if not emp_id or not project_id:
        return jsonify({
            'error': 'employee_id and project_id are required'
        }), 400
    
    # Use mentor agent for employee-specific recommendations
    from agents.mentor import MentorAgent
    mentor = MentorAgent()
    result = mentor.recommend_training(emp_id, project_id)
    
    return jsonify(result)
