# Environment Setup Guide

Complete guide for setting up environment variables for Ulrich AI LMS.

## Quick Reference

| Service | File | Purpose |
|---------|------|---------|
| Backend | `backend/.env` | Local development |
| Backend | Railway Dashboard | Production secrets |
| Frontend | `frontend/.env.local` | Local development |
| Frontend | Vercel Dashboard | Production build vars |

## Local Development Setup

### 1. Backend Environment

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```env
# Application
APP_NAME=Ulrich AI
APP_VERSION=0.1.0
ENVIRONMENT=development

# Database - Choose ONE:
# Option A: Local PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/ulrich_ai

# Option B: Supabase (recommended)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]

# AI Services
OPENAI_API_KEY=sk-proj-[YOUR-KEY]
ANTHROPIC_API_KEY=sk-ant-api03-[YOUR-KEY]

# Vector Database
PINECONE_API_KEY=[YOUR-KEY]
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=ulrich-ai-index

# File Storage
UPLOAD_DIR=uploads

# CORS (for local development)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 2. Frontend Environment

```bash
cd frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

### 3. Verify Setup

Start backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Start frontend:
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 - should see login page.

## Production Deployment

### Railway (Backend)

1. **Create Project** on Railway dashboard
2. **Add Service** → Deploy from GitHub
3. **Set Environment Variables:**

```env
# Required
APP_NAME=Ulrich AI
APP_VERSION=0.1.0
ENVIRONMENT=production

# Database (Railway PostgreSQL plugin OR Supabase)
DATABASE_URL=${DATABASE_URL}  # Auto-filled by Railway if using their PostgreSQL
# OR
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres

SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=[ANON-KEY]

# AI Services (GET THESE FROM YOUR PROVIDERS)
OPENAI_API_KEY=sk-proj-[KEY]
ANTHROPIC_API_KEY=sk-ant-api03-[KEY]

# Vector Database
PINECONE_API_KEY=[KEY]
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=ulrich-ai-production

# CORS (UPDATE AFTER DEPLOYING FRONTEND)
CORS_ORIGINS=https://[YOUR-FRONTEND].vercel.app

# Optional
UPLOAD_DIR=uploads
LOG_LEVEL=info
```

4. **Deploy** - Railway will build from Dockerfile
5. **Note the URL** - e.g., `https://ulrich-backend.up.railway.app`

### Vercel (Frontend)

1. **Import Project** from GitHub
2. **Configure Build:**
   - Framework: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

3. **Set Environment Variables:**

```env
# Required
REACT_APP_API_URL=https://ulrich-backend.up.railway.app
REACT_APP_ENVIRONMENT=production

# Build optimization
NODE_OPTIONS=--max-old-space-size=8192
```

4. **Deploy**
5. **Copy Frontend URL** and update Railway `CORS_ORIGINS`

## Getting API Keys

### Supabase (Database & Auth)
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → API
4. Copy:
   - Project URL → `SUPABASE_URL`
   - Anon/public key → `SUPABASE_KEY`
5. Go to Settings → Database
6. Copy connection string → `DATABASE_URL`

### OpenAI (GPT Models)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account / sign in
3. Go to API Keys
4. Create new secret key → `OPENAI_API_KEY`
5. **Important:** Copy immediately, can't view again

### Anthropic (Claude)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create account / sign in
3. Go to API Keys
4. Create key → `ANTHROPIC_API_KEY`

### Pinecone (Vector Database)
1. Go to [pinecone.io](https://www.pinecone.io)
2. Create account / sign in
3. Create new index:
   - Name: `ulrich-ai-index`
   - Dimensions: 1536 (for OpenAI embeddings)
   - Metric: cosine
4. Go to API Keys
5. Copy:
   - API Key → `PINECONE_API_KEY`
   - Environment → `PINECONE_ENVIRONMENT`
   - Index name → `PINECONE_INDEX_NAME`

## Environment Variable Reference

### Critical (App Won't Work Without These)

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |
| `SUPABASE_URL` | ✅ | - | Supabase project URL |
| `SUPABASE_KEY` | ✅ | - | Supabase anon key |
| `OPENAI_API_KEY` | ✅ | - | For AI chat features |
| `CORS_ORIGINS` | ✅ | - | Comma-separated frontend URLs |
| `REACT_APP_API_URL` | ✅ | - | Backend URL from frontend |

### Important (Features Limited Without These)

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `ANTHROPIC_API_KEY` | ⚠️ | - | Claude fallback for OpenAI |
| `PINECONE_API_KEY` | ⚠️ | - | For RAG/document search |
| `PINECONE_ENVIRONMENT` | ⚠️ | - | Pinecone region |
| `PINECONE_INDEX_NAME` | ⚠️ | - | Vector index name |

### Optional (Nice to Have)

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `APP_NAME` | ❌ | "Ulrich AI" | Display name |
| `ENVIRONMENT` | ❌ | "development" | prod/dev/staging |
| `UPLOAD_DIR` | ❌ | "uploads" | File storage path |
| `LOG_LEVEL` | ❌ | "info" | debug/info/warning/error |
| `SENTRY_DSN` | ❌ | - | Error tracking |
| `REDIS_URL` | ❌ | - | Caching layer |

## Security Best Practices

### ✅ DO

1. **Use environment variables** for ALL secrets
2. **Never commit** `.env` files to git
3. **Rotate keys** quarterly
4. **Use different keys** for dev/staging/production
5. **Limit API key permissions** to minimum required
6. **Monitor usage** to detect key leaks
7. **Set up alerts** for unusual activity

### ❌ DON'T

1. **Never hardcode** API keys in code
2. **Never commit** `.env` files
3. **Never share** production keys in Slack/email
4. **Never use** production keys in development
5. **Never log** environment variables
6. **Never expose** backend env vars to frontend

## Troubleshooting

### "Cannot connect to database"

**Check:**
1. `DATABASE_URL` is set correctly
2. Database is running (Railway, Supabase, or local)
3. Firewall allows connection
4. Credentials are correct

**Test:**
```bash
# From backend directory
python -c "from app.database import engine; print(engine)"
```

### "OpenAI API error: Invalid API key"

**Check:**
1. `OPENAI_API_KEY` starts with `sk-proj-` or `sk-`
2. Key has not been revoked
3. Billing is set up on OpenAI account
4. Usage limits not exceeded

**Test:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### "CORS policy: No 'Access-Control-Allow-Origin'"

**Check:**
1. `CORS_ORIGINS` includes your frontend URL
2. No trailing slash on URLs
3. Protocol matches (http vs https)
4. Backend restarted after changing

**Fix:**
```env
# ❌ Wrong
CORS_ORIGINS=https://app.example.com/

# ✅ Correct
CORS_ORIGINS=https://app.example.com
```

### "Module 'X' not found"

**Check:**
1. All dependencies installed: `pip install -r requirements.txt`
2. Virtual environment activated
3. Running from correct directory

## Migration Checklist

When moving from dev → production:

- [ ] Create new API keys (don't reuse dev keys)
- [ ] Set up production database (Supabase or Railway PostgreSQL)
- [ ] Update `CORS_ORIGINS` with production frontend URL
- [ ] Set `ENVIRONMENT=production`
- [ ] Increase `PINECONE_INDEX_NAME` dimensions if needed
- [ ] Run database migrations
- [ ] Test all integrations
- [ ] Set up monitoring/alerts
- [ ] Document any custom configuration

## Cost Optimization

### Free Tier Limits

| Service | Free Tier | Upgrade Needed When |
|---------|-----------|---------------------|
| Supabase | 500MB DB, 2GB bandwidth | >100 concurrent users |
| OpenAI | Pay-as-you-go | Set budget alerts |
| Anthropic | Pay-as-you-go | Set usage limits |
| Pinecone | 1 index, 100k vectors | >10k documents |
| Railway | $5 credit/month | Hobby projects |
| Vercel | Unlimited | Need custom domain/team |

### Optimization Tips

1. **Cache AI responses** to reduce API calls
2. **Use cheaper models** for simple tasks
3. **Batch vector operations** in Pinecone
4. **Compress images** before upload
5. **Use CDN** for static assets
6. **Monitor costs** weekly

## Support

- **Railway Issues:** [railway.app/help](https://railway.app/help)
- **Vercel Issues:** [vercel.com/support](https://vercel.com/support)
- **API Issues:** Check provider status pages
- **Code Issues:** See PRODUCTION_READINESS.md

---

**Last Updated:** January 2025
**Version:** 1.0.0
