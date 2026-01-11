# BenchCraft AI - Backend Startup Script (Windows PowerShell)
Write-Host "🚀 Starting BenchCraft AI Backend..." -ForegroundColor Cyan

# Navigate to backend directory
Set-Location backend

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    @"
GEMINI_API_KEY=your_gemini_api_key_here
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host "✅ Created .env file. Please edit it and add your Gemini API key!" -ForegroundColor Green
    Write-Host "   Get your key from: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
    Write-Host "   Edit: backend\.env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press any key after adding your API key..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Check if database exists
$dbPath = "..\data\benchcraft.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "Database not found. Seeding database..." -ForegroundColor Cyan
    python seed.py
} else {
    Write-Host "✅ Database already exists." -ForegroundColor Green
}

# Start Flask server
Write-Host ""
Write-Host "🌟 Starting Flask server on http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
python app.py
