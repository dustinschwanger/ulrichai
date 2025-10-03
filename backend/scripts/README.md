# Backend Development Scripts

This directory contains development, testing, and utility scripts. **These scripts are NOT part of the production application.**

## Categories

### Setup Scripts
- `create_admin.py` - Create admin user
- `create_admin_user.py` - Alternative admin creation
- `create_superadmin.py` - Create superadmin user
- `setup_test_data.py` - Populate database with test data
- `setup_test_instructor.py` - Create test instructor account

### Testing Scripts
- `test_auth_api.py` - Test authentication endpoints
- `test_organization_api.py` - Test organization CRUD
- `test_lms_tables.py` - Verify LMS database tables
- `test_quiz_*.py` - Quiz system tests (various aspects)
- `test_course_builder.py` - Course builder functionality
- `test_api_sources.py` - Test API data sources

### Debug Scripts
- `debug_course_creation.py` - Debug course creation issues
- `fix_users.py` - Fix user data issues
- `check_pinecone.py` - Verify Pinecone connection
- `test_openai.py` - Test OpenAI integration
- `test_pinecone.py` - Test Pinecone operations
- `test_prompt.py` - Test AI prompts

### Migration/Utility Scripts
- `migrate_videos_to_supabase.py` - Migrate videos to Supabase storage
- `process_existing_video.py` - Process video files

## Usage

**Important:** Always run scripts from the backend directory:

```bash
cd backend
source venv/bin/activate
python scripts/script_name.py
```

## Production Note

These scripts should **NOT** be deployed to production. They are for development and testing only.

## Converting to Tests

Many of these scripts (`test_*.py`) should eventually be converted to proper unit/integration tests using pytest and moved to a `tests/` directory.
