# Ulrich AI - Learning Management System

AI-powered LMS platform for B2B organizations with deep AI integration for personalized learning experiences.

## 🚀 Quick Start

### Local Development

1. **Clone & Install**
```bash
git clone <your-repo>
cd ulrich-ai

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

2. **Set up Environment**
```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your API keys

# Frontend
cd frontend
cp .env.example .env.local
# Edit .env.local
```

3. **Run Development Servers**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit **http://localhost:3000**

### Using Docker

```bash
# Copy environment template
cp .env.template .env
# Edit .env with your values

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Visit **http://localhost:3000**

## 📚 Documentation

### Essential Guides (START HERE)
- **[PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)** - Complete 4-week roadmap to launch
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Environment variables & API keys
- **[DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)** - Deploy to Railway/Vercel
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Build optimization & troubleshooting

### Additional Docs
- **[LMS_PROJECT_PLAN.md](LMS_PROJECT_PLAN.md)** - Original comprehensive project plan
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Legacy Railway deployment guide
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Local setup instructions

## 🏗️ Project Structure

```
ulrich-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Application entry point
│   │   ├── lms/         # LMS modules (courses, quizzes, etc.)
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
│   ├── scripts/         # Development/admin scripts
│   └── Dockerfile       # Production Docker image
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── features/    # Redux slices
│   │   ├── store/       # Redux store
│   │   └── App.tsx      # Main app component
│   ├── Dockerfile       # Production Docker image
│   └── nginx.conf       # Nginx configuration
│
└── docs/                # Documentation (this folder)
```

## ✨ Features

### Current Features
- ✅ User authentication (Supabase)
- ✅ Course creation & management
- ✅ Multiple activity types (video, reading, quiz, discussion, interactive, embed)
- ✅ Rich text editor for content
- ✅ Drag-and-drop course builder
- ✅ Student progress tracking
- ✅ AI-powered chat assistant
- ✅ Video indexing & RAG
- ✅ Quiz builder with multiple question types
- ✅ Section/Module/Lesson hierarchy

### In Development
- ⏳ File uploads
- ⏳ Enrollment management
- ⏳ Student assignments
- ⏳ Analytics dashboard
- ⏳ Organization management

## 🛠️ Tech Stack

### Frontend
- React 19 + TypeScript
- Material-UI (MUI) v7
- Redux Toolkit + RTK Query
- TipTap (Rich text editor)
- React Router v7
- Vite/CRACO (Build tools)

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- Alembic (Migrations)
- Supabase (Auth & Database)
- PostgreSQL

### AI & ML
- OpenAI GPT-4
- Anthropic Claude
- Pinecone (Vector database)
- OpenAI Whisper (Transcription)

### Infrastructure
- Railway (Backend hosting)
- Vercel (Frontend hosting)
- Supabase (Database & Auth)
- Docker (Containerization)

## 🔧 Configuration

### Required Environment Variables

**Backend:**
- `DATABASE_URL` - PostgreSQL connection
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `OPENAI_API_KEY` - OpenAI API key
- `CORS_ORIGINS` - Allowed frontend URLs

**Frontend:**
- `REACT_APP_API_URL` - Backend URL
- `REACT_APP_ENVIRONMENT` - prod/dev

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for complete reference.

## 📦 Deployment

### Production Deployment (Recommended)

**Option 1: Railway + Vercel (Easiest)**
1. Deploy backend to Railway
2. Deploy frontend to Vercel
3. Update CORS settings

See [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) for step-by-step guide.

**Option 2: Docker (Self-hosting)**
```bash
docker-compose up -d
```

**Option 3: Manual**
- Backend: Any Python WSGI server
- Frontend: Build and serve static files

## 🧪 Testing

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Current Test Coverage
- Backend: Partial (test scripts in `backend/scripts/`)
- Frontend: Minimal (needs expansion)

See PRODUCTION_READINESS.md for testing roadmap.

## 📊 Current Status

### Production Readiness: ~60%

✅ **Completed:**
- Core LMS functionality
- Build optimization
- Environment configuration
- Deployment setup
- Documentation

⏳ **In Progress:**
- Testing framework
- Missing features (enrollments, file uploads)
- Security hardening

❌ **Not Started:**
- Performance optimization
- Comprehensive error handling
- User documentation

See [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) for complete checklist.

## 🐛 Known Issues

1. **Build Memory** - Frontend build fails locally due to memory. Use Railway/Vercel.
2. **No Tests** - Limited test coverage. Manual QA required.
3. **Placeholder Pages** - Some routes show "Coming Soon".
4. **No Rate Limiting** - Add before production.

See GitHub Issues for full list.

## 🤝 Contributing

1. Check [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) for priority tasks
2. Create feature branch
3. Make changes
4. Test locally
5. Submit PR

## 📝 License

[Your License Here]

## 💬 Support

- **Issues:** GitHub Issues
- **Docs:** See documentation files above
- **Deployment Help:** [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)
- **Environment Help:** [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)

## 🗺️ Roadmap

### Phase 1 (Week 1) ✅
- [x] Build optimization
- [x] Code organization
- [x] Deployment configuration

### Phase 2 (Week 2) ⏳
- [ ] Complete missing features
- [ ] Add comprehensive tests
- [ ] Security hardening

### Phase 3 (Week 3) ⏳
- [ ] Performance optimization
- [ ] Complete documentation
- [ ] Staging deployment

### Phase 4 (Week 4) ⏳
- [ ] Production deployment
- [ ] User onboarding
- [ ] Monitoring setup

See [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) for detailed roadmap.

---

**Built with ❤️ for modern learning experiences**

Last Updated: January 2025
