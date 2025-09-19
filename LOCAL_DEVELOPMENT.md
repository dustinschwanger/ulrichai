# Local Development Guide for Ulrich AI

## Quick Start

Run everything with one command:
```bash
./run-local.sh
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000
- API Documentation on http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (first time only):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   # OR
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies (first time only):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies (first time only):**
   ```bash
   npm install
   ```

3. **Run the frontend:**
   ```bash
   npm run dev
   ```

## Environment Files

### Backend (`backend/.env`)
- Contains API keys and database connections
- Already created with your credentials
- Used automatically when running locally

### Frontend (`frontend/.env.local`)
- Points to local backend (http://localhost:8000)
- React automatically uses this for local development
- Production uses `.env.production` instead

## Deployment Control

### Stop Auto-Deployments on Railway

1. **Go to Railway Dashboard**
2. **For each service (backend and frontend):**
   - Navigate to Settings → Service → Deploy
   - Turn OFF "Auto Deploy"
   - Now GitHub pushes won't trigger deployments

3. **Deploy Manually When Ready:**
   - Click "Deploy" button in Railway dashboard
   - OR use Railway CLI: `railway up`

### Alternative: Use Branch-Based Deployments

1. **Create a development branch:**
   ```bash
   git checkout -b dev
   ```

2. **Configure Railway to only deploy from main:**
   - In Railway: Settings → Service → Deploy
   - Set "Branch" to "main" only

3. **Work on dev branch, merge when ready:**
   ```bash
   # On dev branch, make changes
   git add .
   git commit -m "Your changes"
   git push origin dev

   # When ready to deploy
   git checkout main
   git merge dev
   git push origin main  # This triggers deployment
   ```

## Development Workflow

### Daily Development

1. **Start services:**
   ```bash
   ./run-local.sh
   # OR run backend and frontend manually in separate terminals
   ```

2. **Make your changes**
   - Backend changes auto-reload with `--reload` flag
   - Frontend changes auto-reload with React hot reload

3. **Test locally**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Commit and push (won't deploy if auto-deploy is off):**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

### When Ready to Deploy

**Option 1: Manual Deploy (if auto-deploy is off)**
- Go to Railway dashboard
- Click "Deploy" for the service you want to update

**Option 2: Railway CLI**
```bash
railway up
```

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

**Dependencies issues:**
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues

**Port already in use:**
```bash
# Find and kill process on port 3000
lsof -i :3000
kill -9 <PID>
```

**Dependencies issues:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues
- Backend `.env` should have `ENVIRONMENT=development` for local
- Frontend `.env.local` should point to `http://localhost:8000`
- Check backend logs for CORS errors

## Testing Production Build Locally

### Test Frontend Production Build:
```bash
cd frontend
npm run build
npm run serve  # Serves built files on port 3000
```

### Test with Production Environment Variables:
```bash
# Backend
cd backend
ENVIRONMENT=production uvicorn app.main:app

# Frontend (in another terminal)
cd frontend
REACT_APP_API_URL=http://localhost:8000 npm run dev
```

## Useful Commands

### Backend
- `uvicorn app.main:app --reload` - Run with auto-reload
- `pip freeze > requirements.txt` - Update dependencies
- `python -m pytest` - Run tests

### Frontend
- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run test` - Run tests
- `npm run serve` - Serve production build

### Git
- `git status` - Check changes
- `git diff` - View changes
- `git log --oneline -5` - Recent commits
- `git branch` - List branches

## Important Notes

1. **Never commit `.env` files** - They contain sensitive API keys
2. **Production API URL** is in `frontend/.env.production`
3. **Local development** uses different environment files automatically
4. **Backend auto-reloads** when you save Python files
5. **Frontend auto-reloads** when you save React files
6. **Railway deployments** can be controlled via dashboard or CLI

## Support

- Backend API Docs: http://localhost:8000/docs (when running)
- Railway Dashboard: https://railway.app
- Git Repository: https://github.com/dustinschwanger/ulrichai