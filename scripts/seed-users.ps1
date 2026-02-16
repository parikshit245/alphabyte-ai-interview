#!/usr/bin/env pwsh

Write-Host "`n=== Seeding Test Users ===" -ForegroundColor Cyan

$API_URL = "http://localhost:3003/api"

function Register-User {
    param (
        [string]$Email,
        [string]$Password,
        [string]$FirstName,
        [string]$LastName,
        [string]$Role
    )
    
    $body = @{
        email = $Email
        password = $Password
        firstName = $FirstName
        lastName = $LastName
        role = $Role
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "$API_URL/auth/register" `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -ErrorAction Stop
        
        Write-Host "Created $Role account: $Email" -ForegroundColor Green
        return $true
    }
    catch {
        $errorMessage = $_.ErrorDetails.Message
        if ($errorMessage -like "*already exists*" -or $errorMessage -like "*duplicate*") {
            Write-Host "Account already exists: $Email" -ForegroundColor Yellow
        }
        else {
            Write-Host "Failed to create $Role account: $Email" -ForegroundColor Red
            Write-Host "  Error: $errorMessage" -ForegroundColor Red
        }
        return $false
    }
}

Write-Host "`nCreating test accounts..." -ForegroundColor Yellow

# Create Candidate account
Register-User -Email "candidate@test.com" -Password "password123" `
    -FirstName "John" -LastName "Doe" -Role "CANDIDATE"

# Create Recruiter account
Register-User -Email "recruiter@test.com" -Password "password123" `
    -FirstName "Jane" -LastName "Smith" -Role "RECRUITER"

# Create Admin account
Register-User -Email "admin@test.com" -Password "password123" `
    -FirstName "Admin" -LastName "User" -Role "ADMIN"

Write-Host "`n=== Test Accounts Created ===" -ForegroundColor Green
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Candidate Portal (http://localhost:3000/login):" -ForegroundColor White
Write-Host "  Email: candidate@test.com" -ForegroundColor Gray
Write-Host "  Password: password123" -ForegroundColor Gray
Write-Host ""
Write-Host "Recruiter Portal (http://localhost:3001/login):" -ForegroundColor White
Write-Host "  Email: recruiter@test.com" -ForegroundColor Gray
Write-Host "  Password: password123" -ForegroundColor Gray
Write-Host ""
Write-Host "Admin Portal (http://localhost:3002/login):" -ForegroundColor White
Write-Host "  Email: admin@test.com" -ForegroundColor Gray
Write-Host "  Password: password123" -ForegroundColor Gray
Write-Host ""
