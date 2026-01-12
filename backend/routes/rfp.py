"""
RFP Upload and Project Onboarding Routes
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import date, timedelta
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
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Extract data from RFP using parser agent
    # TODO: Replace with dedicated RFP parser agent in production
    try:
        agent = ResumeParserAgent()
        parsed = agent.parse_resume(file_path)
        
        # Map extracted data to project structure
        # For POC, provide dummy/default data if extraction fails
        extracted_data = {
            'client_name': parsed.get('name', 'Sample Client') or 'Sample Client',
            'project_name': parsed.get('project_name') or parsed.get('name', 'New Project') or 'New Project',
            'description': parsed.get('description') or parsed.get('bio_summary', '') or 'Project description extracted from RFP document. This is a sample description for demonstration purposes.',
            'industry_domain': parsed.get('domain', 'FinTech') or 'FinTech',
            'project_type': parsed.get('project_type', 'T&M') or 'T&M',
            'start_date': (date.today() + timedelta(days=30)).isoformat() if not parsed.get('start_date') else parsed.get('start_date'),
            'end_date': (date.today() + timedelta(days=180)).isoformat() if not parsed.get('end_date') else parsed.get('end_date'),
            'status': 'PIPELINE',
            'probability': 75,
            'budget_cap': str(parsed.get('budget', 1000000)) or '1000000',
            'billing_currency': parsed.get('currency', 'USD') or 'USD',
            'tech_stack': parsed.get('skills', []) if isinstance(parsed.get('skills'), list) else (parsed.get('skills', '').split(',') if parsed.get('skills') else ['Python', 'JavaScript', 'React']),
            'team_structure': [
                {'role_name': 'Senior Developer', 'required_count': 2, 'utilization_percentage': 100},
                {'role_name': 'Developer', 'required_count': 1, 'utilization_percentage': 100},
                {'role_name': 'QA Engineer', 'required_count': 1, 'utilization_percentage': 50}
            ]
        }
        
        return jsonify({
            'extracted_data': extracted_data,
            'filename': filename,
            'message': 'RFP data extracted successfully'
        })
    except Exception as e:
        # Fallback: return default structure if parsing fails
        import traceback
        print(f"Error parsing RFP: {e}")
        print(traceback.format_exc())
        
        extracted_data = {
            'client_name': 'Sample Client',
            'project_name': 'New Project',
            'description': 'Project description extracted from RFP document. This is a sample description for demonstration purposes.',
            'industry_domain': 'FinTech',
            'project_type': 'T&M',
            'start_date': (date.today() + timedelta(days=30)).isoformat(),
            'end_date': (date.today() + timedelta(days=180)).isoformat(),
            'status': 'PIPELINE',
            'probability': 75,
            'budget_cap': '1000000',
            'billing_currency': 'USD',
            'tech_stack': ['Python', 'JavaScript', 'React'],
            'team_structure': [
                {'role_name': 'Senior Developer', 'required_count': 2, 'utilization_percentage': 100},
                {'role_name': 'Developer', 'required_count': 1, 'utilization_percentage': 100},
                {'role_name': 'QA Engineer', 'required_count': 1, 'utilization_percentage': 50}
            ]
        }
        
        return jsonify({
            'extracted_data': extracted_data,
            'filename': filename,
            'message': 'RFP uploaded. Using default structure (parsing failed).'
        })
