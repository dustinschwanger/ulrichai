# Deployment Checklist - Ulrich AI LMS

Follow this checklist to deploy to staging/production.

## Pre-Deployment Checklist

### Code Ready ✅
- [x] All changes committed to git
- [x] Code pushed to GitHub
- [x] No sensitive data in repository
- [x] .gitignore properly configured
- [x] Dockerfiles created
- [x] Environment examples documented

### API Keys Collected
Gather these before starting deployment:

**Required:**
- [ ] Supabase URL
- [ ] Supabase Anon Key
- [ ] Supabase Database Connection String
- [ ] OpenAI API Key
- [ ] GitHub repository URL

**Optional but Recommended:**
- [ ] Anthropic API Key
- [ ] Pinecone API Key
- [ ] Pinecone Environment
- [ ] Pinecone Index Name

## Step-by-Step Deployment

### Part 1: Push to GitHub (5 minutes)

```bash
# If not already pushed
git push origin main
```

**Verify:**
- [ ] Code visible on GitHub
- [ ] All recent commits present
- [ ] No .env files in repository

### Part 2: Deploy Backend to Railway (15 minutes)

#### 2.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose **"ulrich-ai"** repository
6. Railway will start analyzing...

#### 2.2 Configure Backend Service

1. Railway will detect the repository
2. Click **"Add Service"** → **"GitHub Repo"**
3. Select your repo again
4. In **Service Settings**:
   - **Service Name:** `ulrich-backend`
   - **Root Directory:** `backend`
   - **Builder:** Dockerfile

#### 2.3 Set Environment Variables

In Railway dashboard → Backend Service → Variables tab:

**Copy/paste this template** (replace with your actual values):

```env
# Application
APP_NAME=Ulrich AI
APP_VERSION=0.1.0
ENVIRONMENT=production

# Database - Supabase
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]

# AI Services
OPENAI_API_KEY=sk-proj-[YOUR-KEY]
ANTHROPIC_API_KEY=sk-ant-[YOUR-KEY]

# Vector Database (if using Pinecone)
PINECONE_API_KEY=[YOUR-KEY]
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=ulrich-ai-production

# CORS (leave blank for now, will update after frontend deploys)
CORS_ORIGINS=

# Optional
UPLOAD_DIR=uploads
LOG_LEVEL=info
```

#### 2.4 Deploy Backend

1. Click **"Deploy"**
2. Wait for build to complete (3-5 minutes)
3. Check deployment logs for errors
4. Once deployed, click **"Settings"** → **"Networking"**
5. **Copy your backend URL** (e.g., `https://ulrich-backend-production.up.railway.app`)

**Verify Backend:**
```bash
# Test health endpoint
curl https://YOUR-BACKEND-URL.railway.app/health
# Should return: {"status":"healthy"}
```

- [ ] Backend deployed successfully
- [ ] Health check passes
- [ ] No errors in logs
- [ ] Backend URL copied

### Part 3: Deploy Frontend to Vercel (10 minutes)

#### 3.1 Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click **"Add New..."** → **"Project"**
4. Click **"Import"** next to your `ulrich-ai` repository

#### 3.2 Configure Build Settings

**Framework Preset:** Create React App

**Root Directory:** `frontend`

**Build Command:** `npm run build`

**Output Directory:** `build`

**Install Command:** `npm install`

#### 3.3 Set Environment Variables

In Vercel → Settings → Environment Variables:

```env
# Required
REACT_APP_API_URL=https://YOUR-BACKEND-URL.railway.app
REACT_APP_ENVIRONMENT=production

# Build optimization
NODE_OPTIONS=--max-old-space-size=8192
```

⚠️ **Replace** `YOUR-BACKEND-URL` with the Railway URL from Step 2.4

#### 3.4 Deploy Frontend

1. Click **"Deploy"**
2. Vercel will build (5-10 minutes - this is normal due to large bundle)
3. Wait for "Building..." → "Deploying..." → "Ready"
4. Click on the deployment URL
5. **Copy your frontend URL** (e.g., `https://ulrich-ai.vercel.app`)

**Verify Frontend:**
- [ ] Frontend loads without errors
- [ ] Login page appears
- [ ] No console errors
- [ ] Frontend URL copied

### Part 4: Update CORS (5 minutes)

#### 4.1 Update Railway Backend

1. Go back to Railway
2. Backend Service → Variables
3. Update `CORS_ORIGINS`:
   ```env
   CORS_ORIGINS=https://ulrich-ai.vercel.app
   ```
   (Use your actual Vercel URL, no trailing slash!)

4. Railway will auto-redeploy (1-2 minutes)

#### 4.2 Test Connection

1. Go to your Vercel URL
2. Try to login
3. Check browser console for errors

**If you see CORS errors:**
- Verify CORS_ORIGINS matches exactly (no trailing /)
- Wait 2 minutes for Railway to redeploy
- Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)

- [ ] CORS configured
- [ ] Backend redeployed
- [ ] Frontend can reach backend

### Part 5: Database Setup (10 minutes)

#### 5.1 Run Migrations

**Option A: Using Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run alembic upgrade head
```

**Option B: Manual (if CLI doesn't work)**
1. In Railway → Backend Service → Settings → Variables
2. Copy the DATABASE_URL
3. Run locally:
```bash
cd backend
export DATABASE_URL="[paste Railway DATABASE_URL]"
alembic upgrade head
```

#### 5.2 Create Admin User

```bash
# Using Railway CLI
railway run python scripts/create_superadmin.py

# Or locally with Railway DB
export DATABASE_URL="[Railway DATABASE_URL]"
python scripts/create_superadmin.py
```

**Save admin credentials!**
- Email: _______________
- Password: _______________

- [ ] Migrations run successfully
- [ ] Admin user created
- [ ] Credentials saved securely

### Part 6: Smoke Testing (15 minutes)

Test these critical paths:

#### 6.1 Authentication
- [ ] Can access frontend URL
- [ ] Can register new user
- [ ] Can login as admin
- [ ] Can logout
- [ ] Can login again

#### 6.2 Course Management (Admin)
- [ ] Can access admin dashboard
- [ ] Can create new course
- [ ] Can add section
- [ ] Can add module
- [ ] Can add lesson
- [ ] Rich text editor works
- [ ] Can save course

#### 6.3 Student View
- [ ] Can view course catalog
- [ ] Can enroll in course
- [ ] Can access course viewer
- [ ] Video plays (if uploaded)
- [ ] Can navigate lessons

#### 6.4 AI Features
- [ ] Chat loads
- [ ] Can send message
- [ ] Receives AI response
- [ ] No errors in console

### Part 7: Monitoring Setup (Optional, 10 minutes)

#### 7.1 Set Up Error Tracking

**Sentry (Recommended)**
1. Go to [sentry.io](https://sentry.io)
2. Create new project
3. Get DSN
4. Add to Railway variables:
   ```env
   SENTRY_DSN=https://[YOUR-DSN]@sentry.io/[PROJECT]
   ```

#### 7.2 Set Up Uptime Monitoring

**UptimeRobot (Free)**
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add monitors:
   - Backend: `https://YOUR-BACKEND.railway.app/health`
   - Frontend: `https://YOUR-FRONTEND.vercel.app`
3. Set alert email

- [ ] Error tracking configured
- [ ] Uptime monitoring active

## Post-Deployment

### Immediate (Day 1)
- [ ] Test all critical user flows
- [ ] Check Railway logs for errors
- [ ] Check Vercel logs for errors
- [ ] Verify database connections
- [ ] Test file uploads
- [ ] Test AI chat
- [ ] Verify emails work (if applicable)

### Week 1
- [ ] Monitor error rates
- [ ] Monitor API usage/costs
- [ ] Gather user feedback
- [ ] Create bug fix backlog
- [ ] Plan iteration 2

## Troubleshooting

### Build Fails on Vercel
**Problem:** Out of memory during build
**Solution:**
- Memory is set to 8GB in NODE_OPTIONS
- If still fails, contact Vercel support
- Or use Railway for frontend too

### Backend Won't Start
**Problem:** Railway deployment fails
**Check:**
1. All environment variables set?
2. DATABASE_URL correct?
3. Check Railway logs for specific error
4. Verify Dockerfile syntax

### Can't Connect to Database
**Problem:** Database connection errors
**Check:**
1. DATABASE_URL format correct?
2. Supabase project active?
3. Firewall rules allow Railway IPs?
4. Connection pooling limits not exceeded?

### CORS Errors
**Problem:** Frontend can't reach backend
**Solution:**
1. Check CORS_ORIGINS exact match
2. No trailing slash
3. Verify backend redeployed after change
4. Hard refresh browser

### 500 Errors on API Calls
**Problem:** Backend crashes on requests
**Check:**
1. Railway logs for Python errors
2. Missing environment variables?
3. Database migrations run?
4. API keys valid?

## Rollback Plan

If deployment has critical issues:

### Rollback Backend
1. Railway → Deployments
2. Find previous working deployment
3. Click "..." → "Redeploy"

### Rollback Frontend
1. Vercel → Deployments
2. Find previous deployment
3. Click "..." → "Promote to Production"

### Rollback Database
```bash
railway run alembic downgrade -1
```

## Cost Monitoring

### Expected Costs (Staging)
- Railway: $5-20/month
- Vercel: $0 (hobby) or $20/month (pro)
- Supabase: $0 (free tier) or $25/month
- OpenAI: Pay-as-you-go (~$10-50/month)
- **Total: $15-115/month**

### Set Budget Alerts
- [ ] OpenAI usage alerts
- [ ] Anthropic usage limits
- [ ] Pinecone usage monitoring
- [ ] Railway spending limits

## Success Criteria

Deployment is successful when:
- [x] Backend health check returns 200
- [x] Frontend loads without errors
- [x] Can create and login user
- [x] Can create course
- [x] Can view course
- [x] AI chat responds
- [x] No critical errors in logs

## Next Steps After Deployment

1. **Configure Custom Domain** (optional)
   - Buy domain
   - Configure DNS
   - Add to Vercel/Railway

2. **Add More Test Data**
   - Create sample courses
   - Add test users
   - Upload test videos

3. **User Acceptance Testing**
   - Share with beta users
   - Gather feedback
   - Create improvement backlog

4. **Iterate**
   - Fix critical bugs
   - Add missing features
   - Optimize performance

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Backend URL:** _______________
**Frontend URL:** _______________
**Status:** ⬜ Success / ⬜ Failed / ⬜ Partial

**Notes:**
