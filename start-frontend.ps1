# BenchCraft AI - Frontend Startup Script (Windows PowerShell)
Write-Host "🚀 Starting BenchCraft AI Frontend..." -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path node_modules)) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
    npm install
} else {
    Write-Host "✅ Dependencies already installed." -ForegroundColor Green
}

# Start Vite dev server
Write-Host ""
Write-Host "🌟 Starting Vite dev server on http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
npm run dev
