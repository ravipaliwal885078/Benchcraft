"""
BenchCraft AI - Flask Application Entry Point
Agentic Internal Talent Marketplace
"""
from flask import Flask
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend
CORS(app)

# Register blueprints
from routes import resources, projects, dashboard, employees, documents, hr, rfp, search, training, risk, monitor, reports, allocation_reports
from routes.employees_skills_risks import bp as employee_skills_risks_bp
app.register_blueprint(resources.bp, url_prefix='/api/v1')
app.register_blueprint(projects.bp, url_prefix='/api/v1')
app.register_blueprint(dashboard.bp, url_prefix='/api/v1')
app.register_blueprint(employees.bp, url_prefix='/api/v1/employees')
app.register_blueprint(employee_skills_risks_bp, url_prefix='/api/v1/employees')
app.register_blueprint(documents.bp, url_prefix='/api/v1/documents')
app.register_blueprint(hr.bp, url_prefix='/api/v1/hr')
app.register_blueprint(rfp.bp, url_prefix='/api/v1/rfp')
app.register_blueprint(search.bp, url_prefix='/api/v1/search')
app.register_blueprint(training.bp, url_prefix='/api/v1/training')
app.register_blueprint(risk.bp, url_prefix='/api/v1/risk')
app.register_blueprint(monitor.bp, url_prefix='/api/v1/monitor')
app.register_blueprint(reports.bp, url_prefix='/api/v1/reports')
app.register_blueprint(allocation_reports.bp, url_prefix='/api/v1/allocation-reports')

@app.route('/')
def health_check():
    return {'status': 'healthy', 'service': 'BenchCraft AI'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
