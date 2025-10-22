# Production Deployment Checklist

This document outlines the steps to prepare the Ulrich AI LMS platform for production deployment.

## ✅ Completed Security Hardening

### 1. JWT Secret Key
- [x] Generated cryptographically secure JWT secret key using `secrets.token_urlsafe(32)`
- [x] Added `JWT_SECRET_KEY` to backend `.env.example`
- [ ] **ACTION REQUIRED**: Set `JWT_SECRET_KEY` in production environment variables

### 2. CORS Configuration
- [x] Removed wildcard CORS origins in production
- [x] Added environment-aware CORS configuration
- [ ] **ACTION REQUIRED**: Set `CORS_ORIGINS` environment variable with exact frontend domain(s)
  ```bash
  CORS_ORIGINS=https://your-frontend.railway.app,https://your-custom-domain.com
  ```

### 3. Rate Limiting
- [x] Installed `slowapi` library
- [x] Added rate limiting to authentication endpoints (5 attempts/minute)
- [x] Configured global rate limiter for FastAPI

### 4. HTTPS Enforcement
- [ ] **ACTION REQUIRED**: Configure HTTPS in production
  - If using Railway: HTTPS is automatic
  - If using custom domain: Configure SSL/TLS certificate
  - Ensure all HTTP requests redirect to HTTPS

## ✅ Completed Analytics Setup

### 1. Google Analytics 4
- [x] Added GA4 script to frontend `index.html`
- [x] Configured page tracking with React Router
- [x] Added TypeScript definitions for `window.gtag`
- [ ] **ACTION REQUIRED**: Get GA4 Measurement ID from https://analytics.google.com/
- [ ] **ACTION REQUIRED**: Set `REACT_APP_GA_MEASUREMENT_ID` environment variable in frontend

### 2. Sentry Error Tracking
- [x] Installed Sentry SDK for React frontend
- [x] Installed Sentry SDK for FastAPI backend
- [x] Configured performance monitoring and session replay
- [x] Added environment-aware sample rates
- [ ] **ACTION REQUIRED**: Create Sentry project at https://sentry.io/
- [ ] **ACTION REQUIRED**: Set `REACT_APP_SENTRY_DSN` in frontend environment variables
- [ ] **ACTION REQUIRED**: Set `SENTRY_DSN` in backend environment variables

### 3. Admin Analytics Dashboard
- [x] Created `/api/lms/admin/analytics/overview` endpoint
- [x] Dashboard returns:
  - Total enrollments
  - Active students
  - Course completion rates
  - Average progress percentages
  - Total courses
  - User counts by role

## 📊 Monitoring & Operations

### Uptime Monitoring

**Recommended Services:**
- [UptimeRobot](https://uptimerobot.com/) - Free tier available
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

**Setup Steps:**
1. Create account with monitoring service
2. Add monitors for:
   - Backend health endpoint: `https://your-backend.railway.app/health`
   - Frontend homepage: `https://your-frontend.railway.app/`
3. Configure alerts:
   - Email notifications for downtime
   - Slack/Discord webhook integration (optional)
4. Set check interval: 5 minutes

### Log Aggregation

**Recommended Services:**
- [Papertrail](https://www.papertrail.com/) - Free tier: 50MB/month
- [Logtail](https://betterstack.com/logtail) - Free tier: 1GB/month
- [Datadog](https://www.datadoghq.com/) - Full observability platform

**Setup Steps:**
1. Create account with log aggregation service
2. Configure Railway to forward logs:
   - Railway Dashboard → Project → Settings → Integrations
   - Or use log drain URLs in Railway environment
3. Set up log filters for:
   - ERROR level logs
   - Authentication failures
   - API errors (4xx, 5xx responses)
4. Create alerts for critical errors

### Database Backups

**Railway PostgreSQL Backups:**
- Railway Pro plan includes automatic daily backups
- Backups retained for 7 days
- Point-in-time recovery available

**Verification Steps:**
1. Log into Railway dashboard
2. Navigate to PostgreSQL service
3. Go to "Backups" tab
4. Verify backups are running daily
5. Test restoration process in development environment

**Supabase Backups:**
- Supabase automatically backs up your database
- Free tier: Daily backups, 7-day retention
- Pro tier: Point-in-time recovery up to 7 days

**Verification Steps:**
1. Log into Supabase dashboard
2. Navigate to Database → Backups
3. Verify daily backups are occurring
4. Review backup size and frequency
5. Document restoration procedure

### Application Performance Monitoring (APM)

**Already Configured:**
- Sentry Performance Monitoring
  - Transaction tracking for API endpoints
  - Frontend performance metrics
  - Sample rate: 100% dev, 10% production

**Additional Options:**
- New Relic APM
- Datadog APM
- Elastic APM

## 🔒 Security Checklist

### Environment Variables
- [ ] All sensitive credentials stored in environment variables (not hardcoded)
- [ ] `.env` files added to `.gitignore`
- [ ] Production environment variables set in Railway/hosting platform
- [ ] Different secrets for development vs production

### Database Security
- [ ] Database uses strong passwords (generated, not default)
- [ ] Database access restricted to application servers only
- [ ] SSL/TLS enabled for database connections
- [ ] Regular security updates applied

### API Security
- [x] Rate limiting enabled on authentication endpoints
- [x] JWT tokens with secure secret key
- [x] CORS restricted to specific origins
- [ ] HTTPS enforced for all API requests
- [ ] Input validation on all endpoints (already using Pydantic)

### User Security
- [x] Passwords hashed using bcrypt
- [x] Minimum password length enforced (8 characters)
- [ ] Consider adding password complexity requirements
- [ ] Consider adding email verification
- [ ] Consider adding 2FA (future enhancement)

## 📦 Deployment Steps

### Backend Deployment (Railway)
1. Create Railway project
2. Add PostgreSQL database
3. Add environment variables:
   ```
   DATABASE_URL (auto-provided by Railway PostgreSQL)
   JWT_SECRET_KEY=<generated-secret>
   SENTRY_DSN=<your-sentry-dsn>
   CORS_ORIGINS=https://your-frontend.railway.app
   ENVIRONMENT=production
   OPENAI_API_KEY=<your-key>
   ANTHROPIC_API_KEY=<your-key>
   PINECONE_API_KEY=<your-key>
   PINECONE_INDEX_NAME=<your-index>
   SUPABASE_URL=<your-url>
   SUPABASE_KEY=<your-key>
   ```
4. Deploy from GitHub repository
5. Run database migrations: `alembic upgrade head`
6. Verify `/health` endpoint returns 200

### Frontend Deployment (Railway/Vercel/Netlify)
1. Create deployment project
2. Add environment variables:
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   REACT_APP_ENVIRONMENT=production
   REACT_APP_GA_MEASUREMENT_ID=<your-ga-id>
   REACT_APP_SENTRY_DSN=<your-sentry-dsn>
   ```
3. Configure build command: `npm run build`
4. Deploy from GitHub repository
5. Verify application loads correctly

## 🧪 Post-Deployment Testing

### Smoke Tests
- [ ] Homepage loads without errors
- [ ] User can register new account
- [ ] User can log in
- [ ] User can view course catalog
- [ ] Admin can access admin dashboard
- [ ] Analytics endpoint returns data
- [ ] Error tracking is working (test with intentional error)

### Performance Tests
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms for most endpoints
- [ ] No memory leaks in long-running sessions
- [ ] Database queries optimized (no N+1 queries)

### Security Tests
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] CORS blocks requests from unauthorized origins
- [ ] Rate limiting triggers after threshold
- [ ] JWT tokens expire correctly
- [ ] Unauthorized users cannot access protected routes

## 📝 Ongoing Maintenance

### Daily
- Check error tracking dashboard (Sentry) for new issues
- Verify uptime monitoring shows 100% availability

### Weekly
- Review application logs for anomalies
- Check database backup status
- Review analytics for usage patterns
- Update dependencies with security patches

### Monthly
- Full security audit
- Review and rotate API keys if needed
- Performance optimization review
- Capacity planning review

## 📞 Incident Response

### Severity Levels
1. **Critical**: Complete outage, data loss, security breach
2. **High**: Major feature broken, significant performance degradation
3. **Medium**: Minor feature broken, some users affected
4. **Low**: Cosmetic issues, minor bugs

### Response Procedures
1. **Detection**: Via monitoring, error tracking, or user reports
2. **Assessment**: Determine severity and impact
3. **Communication**: Notify stakeholders
4. **Resolution**: Deploy fix or rollback
5. **Post-mortem**: Document incident and prevention steps

### Rollback Procedure
1. Identify last known good deployment
2. Revert to previous Railway deployment:
   ```bash
   railway rollback
   ```
3. Verify functionality restored
4. Investigate root cause offline

## 🎯 Success Metrics

Track these metrics to measure platform health:
- **Uptime**: Target 99.9% availability
- **Error Rate**: < 0.1% of requests
- **Page Load Time**: < 3 seconds
- **API Response Time**: < 500ms (p95)
- **User Satisfaction**: Monitor course completion rates
- **Engagement**: Daily/monthly active users

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Google Analytics 4 Documentation](https://developers.google.com/analytics/devguides/collection/ga4)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)
