# Railway Deployment Guide for Ulrich AI

## Quick Start

1. **Fork/Push to GitHub**: Ensure your code is in a GitHub repository
2. **Create Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Deploy from GitHub**: Connect your repository to Railway

## Step-by-Step Deployment

### 1. Repository Preparation

Ensure these files are committed to your repository:
- `railway.toml` (created)
- `backend/Dockerfile` (created)  
- `frontend/Dockerfile` (created)
- `backend/requirements.txt` (created)
- Environment variable templates

### 2. Railway Project Setup

1. **Create New Project**: Click "New Project" in Railway dashboard
2. **Deploy from GitHub**: Select "Deploy from GitHub repo"
3. **Choose Repository**: Select your `ulrich-ai` repository
4. **Service Configuration**: Railway will detect both services automatically

### 3. Environment Variables Configuration

#### Backend Service Variables:
```
APP_NAME=Ulrich AI
APP_VERSION=0.1.0
ENVIRONMENT=production
DATABASE_URL=<Your PostgreSQL URL>
SUPABASE_URL=<Your Supabase URL>
SUPABASE_KEY=<Your Supabase Anon Key>
OPENAI_API_KEY=<Your OpenAI API Key>
ANTHROPIC_API_KEY=<Your Anthropic API Key>
PINECONE_API_KEY=<Your Pinecone API Key>
PINECONE_ENVIRONMENT=<Your Pinecone Environment>
PINECONE_INDEX_NAME=<Your Pinecone Index Name>
CORS_ORIGINS=<Your Frontend Railway URL>
```

#### Frontend Service Variables:
```
REACT_APP_API_URL=<Your Backend Railway URL>
REACT_APP_ENVIRONMENT=production
```

### 4. Database Setup

**Option A: Railway PostgreSQL**
1. Add PostgreSQL addon to your project
2. Use the provided DATABASE_URL in backend environment variables

**Option B: Continue with Supabase**
1. Keep your existing Supabase configuration
2. Ensure SUPABASE_URL and SUPABASE_KEY are set

### 5. File Storage Configuration

Railway provides persistent storage volumes:
1. Go to your backend service settings
2. Add a volume mount for `/app/uploads`
3. This ensures uploaded PDFs persist across deployments

### 6. Custom Domains (Optional)

1. **Backend**: Add custom domain in Railway dashboard
2. **Frontend**: Add custom domain in Railway dashboard  
3. **Update CORS**: Update CORS_ORIGINS with your custom domains
4. **Update Frontend**: Update REACT_APP_API_URL if using custom backend domain

### 7. Post-Deployment Verification

Test these features after deployment:
- [ ] Frontend loads correctly
- [ ] Backend API responds (check /health endpoint)
- [ ] PDF upload functionality works
- [ ] PDF viewer displays documents
- [ ] Chat functionality with AI responses
- [ ] Source cards link to documents
- [ ] Admin panel loads and functions

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Update CORS_ORIGINS in backend environment
2. **PDF Not Loading**: Check REACT_APP_API_URL points to correct backend
3. **File Upload Fails**: Ensure uploads volume is mounted
4. **Database Connection**: Verify DATABASE_URL format
5. **AI Services**: Confirm API keys are set correctly

### Logs Access:
- Backend logs: Railway dashboard → Backend service → Logs
- Frontend logs: Railway dashboard → Frontend service → Logs

### Health Checks:
- Backend: `https://your-backend.railway.app/health`  
- Frontend: `https://your-frontend.railway.app`

## Production Considerations

1. **Environment Variables**: Never commit real API keys to repository
2. **Database Backup**: Set up regular backups for production data
3. **Monitoring**: Set up uptime monitoring for your services
4. **SSL**: Railway provides SSL certificates automatically
5. **Scaling**: Monitor resource usage and scale as needed

## Railway CLI (Optional)

Install Railway CLI for local development:
```bash
npm install -g @railway/cli
railway login
railway link
railway run npm start  # Run with production environment variables
```

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- This deployment configuration supports Railway's latest features and best practices.