# MongoDB Setup Script
# This script helps you set up MongoDB locally for development

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   MongoDB Local Setup Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking for Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker is installed: $dockerVersion" -ForegroundColor Green
    
    # Check if Docker is running
    try {
        docker ps | Out-Null
        Write-Host "[OK] Docker is running" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
    
    # Check if MongoDB container already exists
    $existingContainer = docker ps -a --filter "name=mongodb-ai-interview" --format "{{.Names}}"
    
    if ($existingContainer -eq "mongodb-ai-interview") {
        Write-Host ""
        Write-Host "MongoDB container already exists!" -ForegroundColor Yellow
        $containerStatus = docker ps --filter "name=mongodb-ai-interview" --format "{{.Status}}"
        
        if ($containerStatus) {
            Write-Host "[OK] MongoDB is running" -ForegroundColor Green
        }
        else {
            Write-Host "Starting existing MongoDB container..." -ForegroundColor Yellow
            docker start mongodb-ai-interview
            Start-Sleep -Seconds 3
            Write-Host "[OK] MongoDB started" -ForegroundColor Green
        }
    }
    else {
        Write-Host ""
        Write-Host "Creating MongoDB container..." -ForegroundColor Yellow
        docker run -d `
            --name mongodb-ai-interview `
            -p 27017:27017 `
            -v mongodb_data:/data/db `
            mongo:latest
        
        Start-Sleep -Seconds 5
        Write-Host "[OK] MongoDB container created and started" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "   MongoDB Setup Complete!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Connection URL: mongodb://localhost:27017/ai-interview" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: cd packages/database" -ForegroundColor White
    Write-Host "2. Run: npx prisma db push" -ForegroundColor White
    Write-Host "3. Run: npx prisma generate" -ForegroundColor White
    Write-Host "4. Start your app: pnpm dev" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop MongoDB: docker stop mongodb-ai-interview" -ForegroundColor Gray
    Write-Host "To start MongoDB: docker start mongodb-ai-interview" -ForegroundColor Gray
    
}
catch {
    Write-Host "[ERROR] Docker is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Option 1: Install Docker Desktop" -ForegroundColor Yellow
    Write-Host "Visit: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Install MongoDB Community Server" -ForegroundColor Yellow
    Write-Host "Visit: https://www.mongodb.com/try/download/community" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Install via Chocolatey" -ForegroundColor Yellow
    Write-Host "Run: choco install mongodb" -ForegroundColor White
}
