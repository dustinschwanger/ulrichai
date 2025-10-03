# Production Build Guide

## Current Build Issues

The frontend build currently fails with "heap out of memory" errors even with 16GB+ allocated. This is due to:

1. **Large component files** (CourseEditor.tsx is 1183 lines)
2. **Heavy dependencies** (MUI, TipTap, DnD-Kit, Redux, etc.)
3. **Insufficient code splitting**
4. **No tree shaking optimization**

## Implemented Optimizations

### 1. CRACO Configuration
- Added `craco.config.js` with webpack optimizations
- Configured code splitting by vendor chunks (MUI, TipTap, Redux separate bundles)
- Added esbuild minifier for faster builds

### 2. Route-Based Code Splitting
- Implemented React.lazy() for all major routes in `App.tsx`
- Added Suspense boundaries with loading fallbacks
- Lazy loaded:
  - LMS components (CourseBuilder, CourseEditor, etc.)
  - Chat and Admin components
  - All dashboard and course viewing components

### 3. Memory Configuration
- Updated build script to use 8GB heap size
- Added NODE_OPTIONS environment variable handling

## Required Additional Steps

### Phase 1: Component Refactoring (HIGH PRIORITY)

**CourseEditor.tsx** (1183 lines) needs to be split into:
```
CourseBuilder/
  ├── CourseEditor.tsx (main orchestrator, <200 lines)
  ├── components/
  │   ├── SortableActivity.tsx
  │   ├── SectionEditor.tsx
  │   ├── ModuleEditor.tsx
  │   ├── ActivityList.tsx
  │   └── CourseSettings.tsx
  └── hooks/
      ├── useCourseStructure.ts
      ├── useDragAndDrop.ts
      └── useCourseActions.ts
```

**CourseViewer.tsx** needs similar refactoring:
```
courses/
  ├── CourseViewer.tsx (main, <200 lines)
  ├── components/
  │   ├── VideoContent.tsx
  │   ├── ReadingContent.tsx
  │   ├── InteractiveContent.tsx
  │   ├── QuizContent.tsx
  │   ├── DiscussionContent.tsx
  │   └── EmbedContent.tsx
  └── hooks/
      └── useCourseNavigation.ts
```

### Phase 2: Dependency Optimization

**Reduce bundle size by:**
1. Replace `framer-motion` with CSS transitions (saves ~100KB)
2. Use MUI tree shaking:
   ```js
   // Instead of:
   import { Button } from '@mui/material';
   // Use:
   import Button from '@mui/material/Button';
   ```
3. Consider lighter alternatives:
   - `react-markdown` → `marked` (smaller)
   - `recharts` → `chart.js` or native SVG (lighter)

### Phase 3: Build Infrastructure

**Current approach (temporary):**
```bash
# For development
npm run dev

# For production (may fail)
NODE_OPTIONS="--max-old-space-size=8192" npm run build
```

**Recommended approach for production:**

1. **Use Railway/Vercel build servers** (they have more memory)
2. **Docker multi-stage builds:**
   ```dockerfile
   FROM node:18-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   ENV NODE_OPTIONS="--max-old-space-size=8192"
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/build /usr/share/nginx/html
   ```

3. **Cloud build services:**
   - Netlify (8GB memory limit)
   - Vercel (handles React builds well)
   - Railway (configurable resources)

## Temporary Workaround

Until components are refactored, deploy using:

1. **Railway**: Let Railway handle the build (they have sufficient memory)
2. **Pre-built static files**: Build on a machine with more RAM, commit build folder
3. **Use Vercel/Netlify**: Their build servers can handle larger bundles

## Testing Build Locally

```bash
# Install dependencies
cd frontend
npm install

# Try build (will likely fail locally)
npm run build

# If it fails, deploy to Railway/Vercel instead
git add .
git commit -m "Deploy build"
git push origin main
```

## Production Deployment Steps

1. **Push to GitHub**
2. **Connect to Railway/Vercel**
3. **Set environment variables:**
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   NODE_ENV=production
   ```
4. **Railway will build automatically** with sufficient resources
5. **Monitor build logs** for any errors

## Success Metrics

Build should produce:
- `build/` folder with static assets
- Vendor chunks (mui, redux, tiptap separate)
- Total bundle size < 5MB (gzipped < 1.5MB)
- Build time < 5 minutes

## Next Steps

1. ✅ CRACO configuration created
2. ✅ Code splitting implemented
3. ⏳ Component refactoring (TODO)
4. ⏳ Dependency optimization (TODO)
5. ⏳ Production deployment test (TODO)
