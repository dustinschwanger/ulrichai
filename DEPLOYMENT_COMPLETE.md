# Complete Deployment Guide - Ulrich AI LMS

This guide covers deploying Ulrich AI LMS to production using Railway, Vercel, or Docker.

## Quick Start (Recommended: Railway)

Railway is the easiest option with automatic builds and deployments.

### Prerequisites
- GitHub account
- Railway account (free tier available)
- All API keys ready (OpenAI, Anthropic, Pinecone, Supabase)

### 1. Push to GitHub

```bash
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### 2. Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `ulrich-ai` repository
4. Railway will detect the Dockerfile automatically
5. Set the root directory to `backend`

**Environment Variables to Set:**
```env
# Application
APP_NAME=Ulrich AI
APP_VERSION=0.1.0
ENVIRONMENT=production

# Database (use Railway's PostgreSQL addon OR Supabase)
DATABASE_URL=<Railway will auto-fill if you add PostgreSQL addon>
SUPABASE_URL=<your-supabase-project-url>
SUPABASE_KEY=<your-supabase-anon-key>

# AI Services
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>

# Vector Database
PINECONE_API_KEY=<your-pinecone-key>
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=ulrich-ai-index

# CORS (add your frontend URL after deploying)
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-custom-domain.com
```

6. Click "Deploy" - Railway will build and deploy
7. Note your backend URL (e.g., `https://ulrich-ai-backend.up.railway.app`)

### 3. Deploy Frontend to Vercel (Recommended)

Vercel handles React builds very well with sufficient memory.

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

**Environment Variables:**
```env
REACT_APP_API_URL=https://ulrich-ai-backend.up.railway.app
REACT_APP_ENVIRONMENT=production
NODE_OPTIONS=--max-old-space-size=8192
```

5. Click "Deploy"
6. Note your frontend URL (e.g., `https://ulrich-ai.vercel.app`)

### 4. Update CORS

Go back to Railway backend settings and update `CORS_ORIGINS`:
```env
CORS_ORIGINS=https://ulrich-ai.vercel.app
```

### 5. Run Database Migrations

```bash
# SSH into Railway backend or run locally pointed at production DB
railway run alembic upgrade head
```

### 6. Create Admin User

```bash
# Use the create admin script
railway run python scripts/create_superadmin.py
```

## Alternative: Deploy Frontend to Railway

If you prefer to keep everything on Railway:

1. Create a new Railway service for frontend
2. Point to the same GitHub repo
3. Set root directory to `frontend`
4. Environment variables same as above
5. Railway will build using the Dockerfile

## Alternative: Full Docker Deployment

### Docker Compose (for self-hosting)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Environment Variables Reference

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_NAME` | Application name | `Ulrich AI` |
| `ENVIRONMENT` | Environment type | `production` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon key | `eyJ...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |
| `PINECONE_API_KEY` | Pinecone API key | `xxx-xxx-xxx` |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `us-east-1-aws` |
| `PINECONE_INDEX_NAME` | Pinecone index | `ulrich-ai-index` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://app.example.com` |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://api.example.com` |
| `REACT_APP_ENVIRONMENT` | Environment type | `production` |
| `NODE_OPTIONS` | Node memory allocation | `--max-old-space-size=8192` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_DIR` | File upload directory | `uploads` |
| `LOG_LEVEL` | Logging level | `info` |
| `SENTRY_DSN` | Error tracking | - |
| `REDIS_URL` | Redis for caching | - |

## Post-Deployment Checklist

### Immediate
- [ ] Backend health check: `https://your-backend.railway.app/health`
- [ ] Frontend loads: `https://your-frontend.vercel.app`
- [ ] Can register new user
- [ ] Can login
- [ ] Backend logs show no errors

### Day 1
- [ ] Create admin user
- [ ] Create test course
- [ ] Test course enrollment
- [ ] Test quiz functionality
- [ ] Test video upload/playback
- [ ] Test AI chat

### Week 1
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Configure custom domain
- [ ] Set up SSL certificate (auto on Vercel/Railway)
- [ ] Configure CDN (Cloudflare)
- [ ] Set up automated backups
- [ ] Load testing
- [ ] Security audit

## Monitoring & Maintenance

### Logs

**Railway:**
```bash
railway logs --tail 100
```

**Vercel:**
- View in Vercel dashboard under "Logs" tab

### Health Checks

**Backend:**
```bash
curl https://your-backend.railway.app/health
# Should return: {"status":"healthy"}
```

**Frontend:**
```bash
curl https://your-frontend.vercel.app/health
# Should return: healthy
```

### Common Issues

#### Build Fails (Frontend)
- **Problem:** Out of memory during build
- **Solution:** Vercel has enough memory. If using Railway, increase memory limit in settings.

#### CORS Errors
- **Problem:** Frontend can't reach backend
- **Solution:** Verify `CORS_ORIGINS` includes your frontend URL (no trailing slash)

#### Database Connection Failed
- **Problem:** Can't connect to Supabase
- **Solution:** Check `DATABASE_URL` and `SUPABASE_URL` are correct, and Supabase project is active

#### 500 Errors
- **Problem:** Backend crashes
- **Solution:** Check Railway logs for Python errors. Usually missing environment variables.

## Scaling

### Horizontal Scaling
- Railway: Increase replicas in service settings
- Vercel: Automatic scaling included

### Database
- Railway PostgreSQL: Upgrade plan for more connections
- Supabase: Upgrade for more connections and storage

### Caching
- Add Redis addon on Railway
- Set `REDIS_URL` environment variable
- Backend will automatically use for caching

## Security Hardening

### Required for Production

1. **Enable HTTPS Only** (automatic on Railway/Vercel)
2. **Set Strong CORS Policy:**
   ```env
   CORS_ORIGINS=https://yourdomain.com
   ```
3. **Use Environment Secrets** (never commit .env files)
4. **Add Rate Limiting** (see security guide)
5. **Enable WAF** (Cloudflare in front)

### Recommended

1. **Set up Sentry** for error tracking
2. **Add API authentication** for admin endpoints
3. **Enable database backups** (daily minimum)
4. **Set up monitoring alerts** (Uptime Robot, Pingdom)
5. **Configure CDN** (Cloudflare)

## Rollback Procedure

If deployment fails or has critical bugs:

### Railway
1. Go to service → Deployments
2. Find previous working deployment
3. Click "..." → "Redeploy"

### Vercel
1. Go to Deployments tab
2. Find previous deployment
3. Click "..." → "Promote to Production"

### Database
```bash
# Rollback migrations
railway run alembic downgrade -1
```

## Custom Domain Setup

### Railway (Backend)
1. Settings → Networking → Custom Domain
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS with provided CNAME
4. SSL certificate auto-generates

### Vercel (Frontend)
1. Settings → Domains
2. Add your domain (e.g., `app.yourdomain.com`)
3. Update DNS with provided records
4. SSL certificate auto-generates

## Cost Estimates

### Minimum (Development/MVP)
- Railway: $5/month (backend + PostgreSQL)
- Vercel: Free (hobby tier)
- **Total: ~$5/month**

### Production (100 users)
- Railway: $20/month (pro backend + DB)
- Vercel: Free or $20/month (pro for custom domain)
- Supabase: $25/month (pro tier)
- **Total: ~$45-65/month**

### Scaling (1000+ users)
- Railway: $50/month (increased resources)
- Vercel: $20/month (pro)
- Supabase: $25/month (pro)
- Redis: $10/month
- CDN: $10/month
- **Total: ~$115/month**

## Support & Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Supabase Docs:** https://supabase.com/docs
- **Project Issues:** Check PRODUCTION_READINESS.md

---

**Last Updated:** January 2025
**Deployment Version:** 1.0.0
