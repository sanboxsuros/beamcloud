#!/usr/bin/env pwsh
# Beam vLLM Setup Script for Windows
# Sets up the environment and deploys the vLLM endpoint

Write-Host "🚀 Setting up Beam vLLM deployment for Windows..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
        Write-Host "   Or install from Microsoft Store" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "beam-vllm-env")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv beam-vllm-env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\beam-vllm-env\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install beam-client

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install beam-client" -ForegroundColor Red
    exit 1
}

# Configure Beam with API token
Write-Host "🔑 Configuring Beam..." -ForegroundColor Yellow
Write-Host "Please run the following command to configure your Beam API token:" -ForegroundColor Cyan
Write-Host "beam configure default --token YOUR_API_TOKEN_HERE" -ForegroundColor White
Write-Host ""
Write-Host "Replace YOUR_API_TOKEN_HERE with your actual token:" -ForegroundColor White
Write-Host "bq99X2Wzdgo794QrPfWKgzPwFBl7Zog3ajdiUxTgNOWO1daHRnyRB2nB8zqCFKr8KR9VELgSmzpmhesuidmbpQ==" -ForegroundColor Magenta
Write-Host ""

# Test Beam connection
Write-Host "🧪 Testing Beam connection..." -ForegroundColor Yellow
try {
    beam apps list
} catch {
    Write-Host "⚠️  Beam connection test failed. Please configure your API token first." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Windows setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Configure your API token (see command above)" -ForegroundColor White
Write-Host "2. Activate environment: .\beam-vllm-env\Scripts\Activate.ps1" -ForegroundColor White  
Write-Host "3. Deploy: beam run --gpu A100-40 --memory 16 beam-vllm-setup.py:main" -ForegroundColor White
Write-Host "4. Test: curl https://your-endpoint.app.beam.cloud/" -ForegroundColor White
Write-Host ""
Write-Host "📖 See README.md for detailed instructions and configuration options." -ForegroundColor Cyan