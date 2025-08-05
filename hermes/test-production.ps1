# Hermes Production Test Script

Write-Host "Testing Hermes Production Environment..." -ForegroundColor Green

# Test 1: Check if containers are running
Write-Host "`n1. Checking container status..." -ForegroundColor Yellow
docker compose ps

# Test 2: Check Django application
Write-Host "`n2. Testing Django application..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Django application is responding (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Django application is not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check API documentation
Write-Host "`n3. Testing API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/docs" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ API documentation is accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ API documentation is not accessible" -ForegroundColor Red
}

# Test 4: Check admin interface
Write-Host "`n4. Testing admin interface..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/admin/" -UseBasicParsing -TimeoutSec 10
    if ($response.Content -match "login") {
        Write-Host "✅ Admin interface is accessible (login page)" -ForegroundColor Green
    } else {
        Write-Host "✅ Admin interface is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Admin interface is not accessible" -ForegroundColor Red
}

# Test 5: Check static files
Write-Host "`n5. Testing static files..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/static/admin/css/base.css" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Static files are being served" -ForegroundColor Green
} catch {
    Write-Host "❌ Static files are not being served" -ForegroundColor Red
}

# Test 6: Check Django Unfold CSS
Write-Host "`n6. Testing Django Unfold CSS..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/static/unfold/css/styles.css" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Django Unfold CSS is accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Django Unfold CSS is not accessible" -ForegroundColor Red
}

Write-Host "`n🎉 Production Environment Test Complete!" -ForegroundColor Green
Write-Host "`nAccess your application:" -ForegroundColor Cyan
Write-Host "- Main App: http://localhost:8000" -ForegroundColor White
Write-Host "- Admin: http://localhost:8000/admin/ (admin / HermesAdmin2024!)" -ForegroundColor White
Write-Host "- API Docs: http://localhost:8000/api/docs" -ForegroundColor White 