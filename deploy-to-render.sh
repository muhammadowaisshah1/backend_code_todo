#!/bin/bash
# Render Backend Deployment Script
# This script helps deploy the FastAPI backend to Render

echo "=========================================="
echo "Render Backend Deployment Helper"
echo "=========================================="
echo ""

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "⚠️  Render CLI not found. Installing..."
    echo "Run: npm install -g @render/cli"
    echo ""
fi

# Environment variables to configure
echo "📋 Required Environment Variables:"
echo ""
echo "DATABASE_URL=postgresql://neondb_owner:npg_JIVLmKzCs30W@ep-bold-surf-ah3dx6q5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
echo "BETTER_AUTH_SECRET=iQqaa/xGZmT9Gb0Jh4KEvMJVXghH82rxBk6tqPOsqgQ="
echo "CORS_ORIGINS=https://frontend-psi-ten-81.vercel.app,http://localhost:3000"
echo "DEBUG=false"
echo "JWT_ALGORITHM=HS256"
echo "JWT_EXPIRY_DAYS=7"
echo ""

echo "=========================================="
echo "Deployment Options:"
echo "=========================================="
echo ""
echo "Option 1: Manual Deployment (Recommended)"
echo "  1. Go to https://dashboard.render.com/"
echo "  2. Click 'New +' → 'Web Service'"
echo "  3. Connect your GitHub repository or use 'Deploy from Git'"
echo "  4. Configure:"
echo "     - Name: todo-api-backend"
echo "     - Region: Oregon (US West)"
echo "     - Root Directory: backend"
echo "     - Build Command: pip install -r requirements.txt"
echo "     - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "  5. Add environment variables listed above"
echo "  6. Click 'Create Web Service'"
echo ""

echo "Option 2: Deploy via GitHub"
echo "  1. Create GitHub repository: hackathon-todo-app"
echo "  2. Push code:"
echo "     git remote set-url origin https://github.com/YOUR_USERNAME/hackathon-todo-app.git"
echo "     git push -u origin 001-fullstack-todo-app"
echo "  3. Connect repository to Render"
echo "  4. Render will auto-detect render.yaml"
echo ""

echo "=========================================="
echo "After Deployment:"
echo "=========================================="
echo ""
echo "1. Copy your backend URL (e.g., https://todo-api-backend.onrender.com)"
echo "2. Update frontend environment variable:"
echo "   cd ../frontend"
echo "   vercel env add NEXT_PUBLIC_API_URL production"
echo "   # Enter your backend URL when prompted"
echo "3. Redeploy frontend:"
echo "   vercel --prod --yes --token K30Q70GGtJ3e7ognBDeTNE76"
echo ""
echo "=========================================="
