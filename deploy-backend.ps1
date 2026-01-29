# PowerShell Script for Backend Deployment to Render
# Run this script from the backend directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FastAPI Backend Deployment to Render" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$RENDER_API_KEY = "rnd_f4eZfVGaWjdCx6BbN1uaAVXKSh03"
$OWNER_ID = "tea-cvhvsmpopnds73fojki0"
$GITHUB_REPO = "https://github.com/muhammad-owais-shah/hackathon-todo-app"
$BRANCH = "001-fullstack-todo-app"
$SERVICE_NAME = "hackathon-todo-backend-api"

# Step 1: Verify GitHub Repository
Write-Host "Step 1: Verifying GitHub repository..." -ForegroundColor Yellow
$repoCheck = git ls-remote $GITHUB_REPO 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ GitHub repository not found or not accessible" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create the repository first:" -ForegroundColor Yellow
    Write-Host "1. Go to https://github.com/new" -ForegroundColor White
    Write-Host "2. Repository name: hackathon-todo-app" -ForegroundColor White
    Write-Host "3. Make it Private" -ForegroundColor White
    Write-Host "4. Click 'Create repository'" -ForegroundColor White
    Write-Host ""
    Write-Host "Then push your code:" -ForegroundColor Yellow
    Write-Host "  cd .." -ForegroundColor White
    Write-Host "  git push -u origin 001-fullstack-todo-app" -ForegroundColor White
    Write-Host ""
    exit 1
} else {
    Write-Host "✓ GitHub repository accessible" -ForegroundColor Green
}

# Step 2: Create Render Service
Write-Host ""
Write-Host "Step 2: Creating Render service..." -ForegroundColor Yellow

$servicePayload = @{
    type = "web_service"
    name = $SERVICE_NAME
    ownerId = $OWNER_ID
    repo = $GITHUB_REPO
    branch = $BRANCH
    rootDir = "backend"
    serviceDetails = @{
        env = "python"
        buildCommand = "pip install -r requirements.txt"
        startCommand = "uvicorn main:app --host 0.0.0.0 --port `$PORT"
        healthCheckPath = "/health"
        envVars = @(
            @{
                key = "DATABASE_URL"
                value = "postgresql://neondb_owner:npg_JIVLmKzCs30W@ep-bold-surf-ah3dx6q5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
            },
            @{
                key = "BETTER_AUTH_SECRET"
                value = "iQqaa/xGZmT9Gb0Jh4KEvMJVXghH82rxBk6tqPOsqgQ="
            },
            @{
                key = "CORS_ORIGINS"
                value = "http://localhost:3000,https://*.vercel.app"
            },
            @{
                key = "DEBUG"
                value = "false"
            },
            @{
                key = "JWT_ALGORITHM"
                value = "HS256"
            },
            @{
                key = "JWT_EXPIRY_DAYS"
                value = "7"
            }
        )
    }
    plan = "free"
    region = "oregon"
    autoDeploy = "yes"
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "https://api.render.com/v1/services" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer $RENDER_API_KEY"
            "Content-Type" = "application/json"
        } `
        -Body $servicePayload

    Write-Host "✓ Render service created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service Details:" -ForegroundColor Cyan
    Write-Host "  Name: $($response.service.name)" -ForegroundColor White
    Write-Host "  ID: $($response.service.id)" -ForegroundColor White
    Write-Host "  URL: https://$($response.service.name).onrender.com" -ForegroundColor White
    Write-Host ""

    $serviceId = $response.service.id
    $serviceUrl = "https://$($response.service.name).onrender.com"

    # Step 3: Monitor Deployment
    Write-Host "Step 3: Monitoring deployment..." -ForegroundColor Yellow
    Write-Host "This may take 3-5 minutes..." -ForegroundColor Gray
    Write-Host ""

    $maxAttempts = 60
    $attempt = 0

    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 10
        $attempt++

        try {
            $deploys = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys" `
                -Method Get `
                -Headers @{
                    "Authorization" = "Bearer $RENDER_API_KEY"
                }

            $latestDeploy = $deploys[0]
            $status = $latestDeploy.status

            Write-Host "[$attempt/$maxAttempts] Status: $status" -ForegroundColor Gray

            if ($status -eq "live") {
                Write-Host ""
                Write-Host "✓ Deployment successful!" -ForegroundColor Green
                break
            } elseif ($status -eq "build_failed" -or $status -eq "deactivated") {
                Write-Host ""
                Write-Host "❌ Deployment failed with status: $status" -ForegroundColor Red
                Write-Host "Check logs at: https://dashboard.render.com/web/$serviceId" -ForegroundColor Yellow
                exit 1
            }
        } catch {
            Write-Host "Error checking deployment status: $_" -ForegroundColor Red
        }
    }

    if ($attempt -eq $maxAttempts) {
        Write-Host ""
        Write-Host "⚠️  Deployment timeout. Check status at: https://dashboard.render.com/web/$serviceId" -ForegroundColor Yellow
    }

    # Step 4: Verify Deployment
    Write-Host ""
    Write-Host "Step 4: Verifying deployment..." -ForegroundColor Yellow

    Start-Sleep -Seconds 5

    try {
        $healthCheck = Invoke-RestMethod -Uri "$serviceUrl/health" -Method Get
        Write-Host "✓ Health check passed: $($healthCheck.status)" -ForegroundColor Green

        $rootCheck = Invoke-RestMethod -Uri "$serviceUrl/" -Method Get
        Write-Host "✓ Root endpoint working: $($rootCheck.app_name) v$($rootCheck.version)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Could not verify endpoints (service may still be starting)" -ForegroundColor Yellow
        Write-Host "   Try manually: $serviceUrl/health" -ForegroundColor Gray
    }

    # Final Report
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✓ Live API URL: $serviceUrl" -ForegroundColor Green
    Write-Host "✓ Service ID: $serviceId" -ForegroundColor Green
    Write-Host "✓ GitHub Repo: $GITHUB_REPO" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Test API: $serviceUrl/docs" -ForegroundColor White
    Write-Host "2. Update frontend NEXT_PUBLIC_API_URL to: $serviceUrl" -ForegroundColor White
    Write-Host "3. Monitor logs: https://dashboard.render.com/web/$serviceId" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "❌ Error creating Render service:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Fallback: Deploy manually via Render Dashboard" -ForegroundColor Yellow
    Write-Host "See RENDER_DEPLOYMENT_GUIDE.md for instructions" -ForegroundColor White
    exit 1
}
