#!/usr/bin/env pwsh
# Docker deployment script for AI Interview Intelligence Platform

Write-Host "`n=== AI Interview Intelligence Platform - Docker Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker is running" -ForegroundColor Green

# Stop and remove existing containers
Write-Host "`nStopping existing containers..." -ForegroundColor Yellow
docker compose down -v 2>$null

# Build and start all services
Write-Host "`nBuilding and starting all services..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes on first run..." -ForegroundColor Yellow
Write-Host ""

docker compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== ✓ Platform Started Successfully ===" -ForegroundColor Green
    Write-Host "`nServices:" -ForegroundColor Cyan
    Write-Host "  • Backend API:       http://localhost:3003" -ForegroundColor White
    Write-Host "  • Candidate Portal:  http://localhost:3000" -ForegroundColor White
    Write-Host "  • Recruiter Portal:  http://localhost:3001" -ForegroundColor White
    Write-Host "  • Admin Portal:      http://localhost:3002" -ForegroundColor White
    Write-Host "`nView logs:" -ForegroundColor Cyan
    Write-Host "  docker compose logs -f" -ForegroundColor Gray
    Write-Host "`nStop all services:" -ForegroundColor Cyan
    Write-Host "  docker compose down" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "`n✗ Failed to start services" -ForegroundColor Red
    exit 1
}
