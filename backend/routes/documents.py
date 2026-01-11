"""
Document Management Routes
Handles resume and certificate uploads for onboarding
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from agents.resume_parser_agent import ResumeParserAgent
from agents.skill_detection_agent import SkillDetectionAgent

bp = Blueprint('documents', __name__)
UPLOAD_FOLDER = 'data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/upload/resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Parse resume using agent
    agent = ResumeParserAgent()
    parsed = agent.parse_resume(file_path)

    # Skill detection
    skill_agent = SkillDetectionAgent()
    skills = skill_agent.detect_skills(parsed.get('skills', ''))
    parsed['skills_detected'] = skills
    return jsonify({'parsed': parsed, 'filename': filename})

@bp.route('/upload/certificate', methods=['POST'])
def upload_certificate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Stub: Certificate validation logic
    # In production, use document_validator tool
    cert_data = {
        'issuer': 'Coursera',
        'date': '2025-01-01',
        'skill': 'AI',
        'valid': True
    }
    return jsonify({'certificate': cert_data, 'filename': filename})
