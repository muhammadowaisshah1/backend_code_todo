# Render Deployment Guide - FastAPI Backend

## Prerequisites Completed
- Backend code is production-ready
- Dockerfile exists and configured
- Environment variables validated
- Database (Neon PostgreSQL) is set up

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `hackathon-todo-backend-api`
3. Description: `FastAPI backend for full-stack todo application - Phase 2 Hackathon`
4. Visibility: **Private** (recommended)
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

## Step 2: Push Code to GitHub

Run these commands from the project root:

```bash
cd "D:\hackathoons\Hackthon_Full-Stack_App"

# Update remote URL to new repository
git remote set-url origin https://github.com/YOUR_USERNAME/hackathon-todo-backend-api.git

# Push current branch
git push -u origin 001-fullstack-todo-app

# Or push to main branch
git checkout -b main
git push -u origin main
```

## Step 3: Deploy to Render

### Option A: Via Render Dashboard (Easiest)

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** or **"Build and deploy from a Git repository"**
4. Select your repository: `hackathon-todo-backend-api`
5. Configure the service:

**Basic Settings:**
- **Name:** `hackathon-todo-backend-api`
- **Region:** Oregon (US West) or closest to you
- **Branch:** `001-fullstack-todo-app` or `main`
- **Root Directory:** `backend`
- **Runtime:** Python 3

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Health Check Path:** `/health`
- **Auto-Deploy:** Yes

6. Click **"Advanced"** and add environment variables:

```
DATABASE_URL=postgresql://neondb_owner:npg_JIVLmKzCs30W@ep-bold-surf-ah3dx6q5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

BETTER_AUTH_SECRET=iQqaa/xGZmT9Gb0Jh4KEvMJVXghH82rxBk6tqPOsqgQ=

CORS_ORIGINS=http://localhost:3000,https://*.vercel.app

DEBUG=false

JWT_ALGORITHM=HS256

JWT_EXPIRY_DAYS=7
```

7. Click **"Create Web Service"**

### Option B: Via Render API

Once the GitHub repository exists, run:

```bash
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer rnd_f4eZfVGaWjdCx6BbN1uaAVXKSh03" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "hackathon-todo-backend-api",
    "ownerId": "tea-cvhvsmpopnds73fojki0",
    "repo": "https://github.com/YOUR_USERNAME/hackathon-todo-backend-api",
    "branch": "001-fullstack-todo-app",
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
  }'
```

## Step 4: Monitor Deployment

1. Go to your service in Render dashboard
2. Click on **"Logs"** tab
3. Watch for:
   - ✓ Build started
   - ✓ Dependencies installed
   - ✓ Build completed
   - ✓ Service starting
   - ✓ "Starting up: Creating database tables..."
   - ✓ "Database tables created successfully"
   - ✓ Server running on port

Deployment typically takes 3-5 minutes.

## Step 5: Verify Deployment

Once deployment shows "Live", test your API:

```bash
# Get your service URL from Render dashboard (e.g., https://hackathon-todo-backend-api.onrender.com)

# Test root endpoint
curl https://YOUR_SERVICE_URL.onrender.com/

# Expected response:
# {
#   "status": "healthy",
#   "app_name": "Todo API",
#   "version": "1.0.0",
#   "timestamp": "2026-01-29T..."
# }

# Test health endpoint
curl https://YOUR_SERVICE_URL.onrender.com/health

# Expected response:
# {"status": "healthy"}

# Test API documentation
# Open in browser: https://YOUR_SERVICE_URL.onrender.com/docs
```

## Step 6: Update Frontend

Once backend is deployed, update your frontend environment variable:

```bash
cd frontend

# Add production API URL
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://YOUR_SERVICE_URL.onrender.com

# Redeploy frontend
vercel --prod
```

## Troubleshooting

### Build Fails
- Check logs for missing dependencies
- Verify `requirements.txt` is complete
- Ensure Python version compatibility

### Service Won't Start
- Check start command uses `$PORT` variable
- Verify `main.py` exists in backend directory
- Check logs for import errors

### Database Connection Fails
- Verify `DATABASE_URL` includes `?sslmode=require`
- Check Neon database is active
- Verify connection string credentials

### Health Check Fails
- Ensure `/health` endpoint exists in `main.py`
- Check service is binding to `0.0.0.0:$PORT`
- Verify no firewall blocking health checks

## Important Notes

1. **Free Tier Limitations:**
   - Service spins down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds
   - 750 hours/month free (sufficient for development)

2. **Auto-Deploy:**
   - Enabled by default
   - Any push to the connected branch triggers redeployment
   - Monitor deployments in Render dashboard

3. **Environment Variables:**
   - Never commit `.env` to Git
   - Update via Render dashboard or API
   - Changes require service restart

4. **CORS Configuration:**
   - Update `CORS_ORIGINS` with your frontend URL after deployment
   - Format: `https://your-frontend.vercel.app,http://localhost:3000`

## Next Steps

After successful deployment:

1. Test all API endpoints via `/docs`
2. Update frontend with backend URL
3. Test end-to-end authentication flow
4. Monitor logs for any errors
5. Set up custom domain (optional)

## Support

- Render Documentation: https://render.com/docs
- Render Status: https://status.render.com/
- API Reference: https://api-docs.render.com/

---

**Deployment Status:** Ready for deployment
**Last Updated:** 2026-01-29
