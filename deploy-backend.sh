#!/bin/bash
# Bash Script for Backend Deployment to Render
# Run this script from the backend directory

set -e

echo "========================================"
echo "FastAPI Backend Deployment to Render"
echo "========================================"
echo ""

# Configuration
RENDER_API_KEY="rnd_f4eZfVGaWjdCx6BbN1uaAVXKSh03"
OWNER_ID="tea-cvhvsmpopnds73fojki0"
GITHUB_REPO="https://github.com/muhammad-owais-shah/hackathon-todo-app"
BRANCH="001-fullstack-todo-app"
SERVICE_NAME="hackathon-todo-backend-api"

# Step 1: Verify GitHub Repository
echo "Step 1: Verifying GitHub repository..."
if ! git ls-remote "$GITHUB_REPO" &> /dev/null; then
    echo "❌ GitHub repository not found or not accessible"
    echo ""
    echo "Please create the repository first:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: hackathon-todo-app"
    echo "3. Make it Private"
    echo "4. Click 'Create repository'"
    echo ""
    echo "Then push your code:"
    echo "  cd .."
    echo "  git push -u origin 001-fullstack-todo-app"
    echo ""
    exit 1
else
    echo "✓ GitHub repository accessible"
fi

# Step 2: Create Render Service
echo ""
echo "Step 2: Creating Render service..."

RESPONSE=$(curl -s -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "'"$SERVICE_NAME"'",
    "ownerId": "'"$OWNER_ID"'",
    "repo": "'"$GITHUB_REPO"'",
    "branch": "'"$BRANCH"'",
    "rootDir": "backend",
    "serviceDetails": {
      "env": "python",
      "buildCommand": "pip install -r requirements.txt",
      "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
      "healthCheckPath": "/health",
      "envVars": [
        {
          "key": "DATABASE_URL",
          "value": "postgresql://neondb_owner:npg_JIVLmKzCs30W@ep-bold-surf-ah3dx6q5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
        },
        {
          "key": "BETTER_AUTH_SECRET",
          "value": "iQqaa/xGZmT9Gb0Jh4KEvMJVXghH82rxBk6tqPOsqgQ="
        },
        {
          "key": "CORS_ORIGINS",
          "value": "http://localhost:3000,https://*.vercel.app"
        },
        {
          "key": "DEBUG",
          "value": "false"
        },
        {
          "key": "JWT_ALGORITHM",
          "value": "HS256"
        },
        {
          "key": "JWT_EXPIRY_DAYS",
          "value": "7"
        }
      ]
    },
    "plan": "free",
    "region": "oregon",
    "autoDeploy": "yes"
  }')

# Check for errors
if echo "$RESPONSE" | grep -q '"message"'; then
    echo "❌ Error creating Render service:"
    echo "$RESPONSE" | grep -o '"message":"[^"]*"'
    echo ""
    echo "Fallback: Deploy manually via Render Dashboard"
    echo "See RENDER_DEPLOYMENT_GUIDE.md for instructions"
    exit 1
fi

SERVICE_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
SERVICE_URL="https://$SERVICE_NAME.onrender.com"

echo "✓ Render service created successfully!"
echo ""
echo "Service Details:"
echo "  Name: $SERVICE_NAME"
echo "  ID: $SERVICE_ID"
echo "  URL: $SERVICE_URL"
echo ""

# Step 3: Monitor Deployment
echo "Step 3: Monitoring deployment..."
echo "This may take 3-5 minutes..."
echo ""

MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))

    DEPLOYS=$(curl -s -X GET "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
      -H "Authorization: Bearer $RENDER_API_KEY")

    STATUS=$(echo "$DEPLOYS" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

    echo "[$ATTEMPT/$MAX_ATTEMPTS] Status: $STATUS"

    if [ "$STATUS" = "live" ]; then
        echo ""
        echo "✓ Deployment successful!"
        break
    elif [ "$STATUS" = "build_failed" ] || [ "$STATUS" = "deactivated" ]; then
        echo ""
        echo "❌ Deployment failed with status: $STATUS"
        echo "Check logs at: https://dashboard.render.com/web/$SERVICE_ID"
        exit 1
    fi
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo ""
    echo "⚠️  Deployment timeout. Check status at: https://dashboard.render.com/web/$SERVICE_ID"
fi

# Step 4: Verify Deployment
echo ""
echo "Step 4: Verifying deployment..."

sleep 5

if curl -sf "$SERVICE_URL/health" > /dev/null; then
    echo "✓ Health check passed"
else
    echo "⚠️  Health check failed (service may still be starting)"
fi

if curl -sf "$SERVICE_URL/" > /dev/null; then
    echo "✓ Root endpoint working"
else
    echo "⚠️  Root endpoint not responding yet"
fi

# Final Report
echo ""
echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "✓ Live API URL: $SERVICE_URL"
echo "✓ Service ID: $SERVICE_ID"
echo "✓ GitHub Repo: $GITHUB_REPO"
echo ""
echo "Next Steps:"
echo "1. Test API: $SERVICE_URL/docs"
echo "2. Update frontend NEXT_PUBLIC_API_URL to: $SERVICE_URL"
echo "3. Monitor logs: https://dashboard.render.com/web/$SERVICE_ID"
echo ""
