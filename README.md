# BenchCraft AI: Agentic Internal Talent Marketplace

An "Active Market Maker" for internal resource allocation that solves the "Bench Burn" problem by replacing static spreadsheets with an Agentic Workspace.

## Features

- **Blind Allocation**: Query resources using natural language JDs with anonymized results
- **Bench Burn Dashboard**: Real-time visualization of idle employee costs
- **Ghost Teams**: Preview team compositions for upcoming deals
- **Resume Tailor**: AI-generated client-specific bio PDFs
- **AI Career Path**: Personalized training recommendations

## Tech Stack

- **Backend**: Flask, SQLAlchemy, CrewAI, ChromaDB, Google Gemini
- **Frontend**: React, Vite, Tailwind CSS, Recharts, React Flow

## Quick Start

### Windows (Recommended)

Use the provided PowerShell scripts:

```powershell
# Terminal 1 - Backend
.\start-backend.ps1

# Terminal 2 - Frontend  
.\start-frontend.ps1
```

### Manual Setup

See [SETUP.md](SETUP.md) for detailed setup instructions (Mac/Linux) or [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for Windows-specific guide with C++ Build Tools installation.

## Environment Variables

Create a `.env` file in the `backend` directory:

```
GEMINI_API_KEY=your_gemini_api_key
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Project Structure

```
/benchcraft-ai
  /backend
    /agents      # CrewAI Agent Definitions
    /tools        # Agent Tools
    /routes       # REST API Controllers
  /frontend
    /src
      /components
      /pages
      /services
  /data          # SQLite DB and ChromaDB storage
```

## Documentation

- [SETUP.md](SETUP.md) - Detailed setup guide for all platforms
- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows-specific setup with C++ Build Tools instructions

## Development Phases

See BENCHCRAFT_MASTER_SPEC.md for detailed development roadmap.
