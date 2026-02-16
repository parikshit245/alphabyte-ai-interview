#!/usr/bin/env pwsh

Write-Host "Validating AI Interview Platform Setup..." -ForegroundColor Cyan
Write-Host ""

# Check Node version
Write-Host "Checking Node.js version..." -NoNewline
$nodeVersion = node --version
if ($nodeVersion -match "v(\d+)\.") {
    $majorVersion = [int]$matches[1]
    if ($majorVersion -ge 20) {
        Write-Host " ✓ $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host " ✗ Node.js 20+ required (found $nodeVersion)" -ForegroundColor Red
        exit 1
    }
}

# Check pnpm
Write-Host "Checking pnpm..." -NoNewline
try {
    $pnpmVersion = pnpm --version
    Write-Host " ✓ v$pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host " ✗ pnpm not found" -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "Checking Docker..." -NoNewline
try {
    $dockerVersion = docker --version
    Write-Host " ✓" -ForegroundColor Green
} catch {
    Write-Host " ✗ Docker not found" -ForegroundColor Red
    exit 1
}

# Type checking
Write-Host ""
Write-Host "Running TypeScript type check..." -ForegroundColor Yellow
pnpm type-check

if ($LASTEXITCODE -ne 0) {
    Write-Host "Type check failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Validation complete! ✓" -ForegroundColor Green
