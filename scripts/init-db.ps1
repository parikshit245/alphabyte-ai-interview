#!/usr/bin/env pwsh

Write-Host "Initializing AI Interview Platform Database..." -ForegroundColor Green

# Wait for CockroachDB to be ready
Write-Host "Waiting for CockroachDB to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health?ready=1" -Method Get -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "CockroachDB is ready!" -ForegroundColor Green
            break
        }
    }
    catch {
        $attempt++
        Write-Host "Attempt $attempt/$maxAttempts - Waiting for CockroachDB..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "Failed to connect to CockroachDB after $maxAttempts attempts" -ForegroundColor Red
    exit 1
}

# Create database if it doesn't exist
Write-Host "Creating database..." -ForegroundColor Yellow
docker exec interview-platform-db ./cockroach sql --insecure --execute="CREATE DATABASE IF NOT EXISTS interview_platform;"

# Run Prisma migrations
Write-Host "Running Prisma migrations..." -ForegroundColor Yellow
Set-Location -Path "packages/database"
npx prisma db push --skip-generate
Set-Location -Path "../.."

Write-Host "Database initialization complete!" -ForegroundColor Green
