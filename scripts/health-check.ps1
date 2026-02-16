#!/usr/bin/env pwsh

Write-Host "AI Interview Platform - Health Check" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{ Name = "CockroachDB Admin UI"; Url = "http://localhost:8080/health?ready=1"; Port = 8080 },
    @{ Name = "Backend API"; Url = "http://localhost:3003/api/health"; Port = 3003 },
    @{ Name = "Candidate Portal"; Url = "http://localhost:3000"; Port = 3000 },
    @{ Name = "Recruiter Portal"; Url = "http://localhost:3001"; Port = 3001 },
    @{ Name = "Admin Portal"; Url = "http://localhost:3002"; Port = 3002 }
)

$allHealthy = $true

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)... " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $service.Url -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Healthy" -ForegroundColor Green
        } else {
            Write-Host "✗ Unhealthy (Status: $($response.StatusCode))" -ForegroundColor Red
            $allHealthy = $false
        }
    }
    catch {
        Write-Host "✗ Not responding" -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host ""
if ($allHealthy) {
    Write-Host "All services are healthy! ✓" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some services are not healthy. Please check the logs." -ForegroundColor Yellow
    exit 1
}
