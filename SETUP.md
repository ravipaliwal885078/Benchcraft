# BenchCraft AI Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API Key (Get from https://makersuite.google.com/app/apikey)

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
# Edit .env and add your GEMINI_API_KEY

# Initialize database and seed data
python seed.py

# Run Flask server
python app.py
```

The backend will run on `http://localhost:5000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

## Project Structure

```
benchcraft-ai/
├── backend/
│   ├── agents/          # CrewAI agents
│   ├── tools/           # Database and vector tools
│   ├── routes/          # API endpoints
│   ├── models.py        # SQLAlchemy models
│   ├── seed.py          # Database seeding
│   └── app.py           # Flask app entry
├── frontend/
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page components
│       └── services/    # API client
└── data/                # SQLite DB and ChromaDB storage
```

## API Endpoints

- `POST /api/v1/search` - Blind talent search
- `POST /api/v1/allocate` - Allocate resource to project
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/kpi` - Dashboard KPIs

## Features Implemented

✅ Database models (all 6 tables)
✅ ChromaDB vector search integration
✅ CrewAI agents (Scout, Matchmaker, Auditor, Mentor, Ghostwriter)
✅ Blind allocation with anonymization
✅ Bench burn dashboard
✅ Project pipeline management
✅ Frontend UI with all pages

## Next Steps

1. Add authentication/authorization
2. Implement full Canvas timeline view
3. Add PDF generation for tailored bios
4. Enhance training recommendations
5. Add real-time notifications
6. Implement advanced filtering
