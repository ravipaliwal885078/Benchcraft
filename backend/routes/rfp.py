"""
RFP Upload and Project Onboarding Routes
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from agents.resume_parser_agent import ResumeParserAgent  # Placeholder for RFP parser agent

bp = Blueprint('rfp', __name__)
UPLOAD_FOLDER = 'data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/upload', methods=['POST'])
def upload_rfp():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Stub: Use RFP parser agent to extract project data
    # Replace ResumeParserAgent with RFPParserAgent in production
    agent = ResumeParserAgent()
    parsed = agent.parse_resume(file_path)
    project_data = {
        'project_name': parsed.get('name', 'New Project'),
        'description': parsed.get('bio_summary', ''),
        'skills': parsed.get('skills', []),
        'budget': 100000,
        'timeline': '6 months',
        'domain': 'IT'
    }
    return jsonify({'project': project_data, 'filename': filename})
