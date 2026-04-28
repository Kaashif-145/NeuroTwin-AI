# NeuroTwin AI Starter Script
# This script activates the virtual environment and starts the Streamlit app.

if (Test-Path ".venv") {
    Write-Host "🚀 Activating Virtual Environment..." -ForegroundColor Cyan
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ Warning: .venv folder not found. Running in default environment." -ForegroundColor Yellow
}

Write-Host "🌌 Starting NeuroTwin AI Dashboard..." -ForegroundColor Magenta
streamlit run frontend/app.py
