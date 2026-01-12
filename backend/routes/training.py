"""
Training and Skill Gap Analysis Route
Upskilling recommendations over hiring
"""
from flask import Blueprint, request, jsonify
import traceback

bp = Blueprint('training', __name__)

# Initialize agent (singleton pattern) - lazy loading to avoid startup errors
_training_agent = None

def get_training_agent():
    """Get or create training recommendation agent with error handling"""
    global _training_agent
    if _training_agent is None:
        try:
            from agents.training_recommendation_agent import TrainingRecommendationAgent
            _training_agent = TrainingRecommendationAgent()
        except Exception as e:
            print(f"Warning: Failed to initialize TrainingRecommendationAgent: {e}")
            traceback.print_exc()
            raise
    return _training_agent

@bp.route('/test', methods=['GET'])
def test_training_route():
    """Test endpoint to verify training routes are working"""
    return jsonify({
        'message': 'Training routes are working',
        'route': '/api/v1/training/test'
    })

@bp.route('/recommendations', methods=['GET'])
def get_training_recommendations():
    """
    Get AI-powered training recommendations for upcoming projects
    Analyzes skill gaps and recommends upskilling over hiring
    """
    try:
        # Initialize agent with error handling
        try:
            agent = get_training_agent()
        except Exception as agent_error:
            error_traceback = traceback.format_exc()
            print(f"Error initializing TrainingRecommendationAgent: {error_traceback}")
            return jsonify({
                'error': f'Failed to initialize AI agent: {str(agent_error)}',
                'traceback': error_traceback,
                'message': 'Please check backend logs for details'
            }), 500
        
        # Call agent method
        try:
            result = agent.analyze_skill_gaps_and_recommend_training()
            return jsonify(result)
        except Exception as analysis_error:
            error_traceback = traceback.format_exc()
            print(f"Error analyzing skill gaps: {error_traceback}")
            return jsonify({
                'error': str(analysis_error),
                'traceback': error_traceback,
                'message': 'Failed to generate training recommendations'
            }), 500
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Unexpected error in get_training_recommendations: {error_traceback}")
        return jsonify({
            'error': str(e),
            'traceback': error_traceback,
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
