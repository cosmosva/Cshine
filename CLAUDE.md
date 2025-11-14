# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Cshine** is an AI-powered voice recording and idea management tool built as a WeChat Mini Program with a FastAPI backend. The project enables users to capture ideas through voice, automatically transcribe them using Alibaba Cloud Tingwu, and generate intelligent summaries with configurable LLM providers.

## Architecture

### Three-Tier Structure

```
miniprogram/    # WeChat Mini Program (Frontend)
backend/        # FastAPI REST API (Backend)
web/            # Web Admin Portal (Static HTML/Bootstrap)
```

### Technology Stack

**Frontend (WeChat Mini Program)**
- Native WeChat Mini Program development (JavaScript ES6+, WXSS)
- Custom component system: navigation-bar, record-button, flash-card, ai-model-picker, waveform-player, mindmap, upload-modal
- Network layer: [miniprogram/utils/request.js](miniprogram/utils/request.js) with JWT authentication
- API abstraction: [miniprogram/utils/api.js](miniprogram/utils/api.js)

**Backend (Python FastAPI)**
- Python 3.11+ with FastAPI 0.121.0, SQLAlchemy 2.0.44
- Database: SQLite (dev) / PostgreSQL (production via `DATABASE_URL` env var)
- Authentication: JWT tokens (7-day expiry) via python-jose
- File storage: Aliyun OSS
- AI services: Alibaba Cloud Tingwu (ASR), multiple LLM providers (OpenAI, Anthropic, Qwen, Doubao)
- Async processing: Python threading for background AI tasks

**Key Backend Files**
- [backend/main.py](backend/main.py) - Application entry point
- [backend/config.py](backend/config.py) - Pydantic settings (loads from .env)
- [backend/app/models.py](backend/app/models.py) - SQLAlchemy models
- [backend/app/schemas.py](backend/app/schemas.py) - Pydantic request/response schemas
- [backend/app/api/](backend/app/api/) - Modular API routers

### Database Schema

Core tables:
- `users` - User authentication and profiles
- `flashes` - Quick voice recordings with AI processing
- `meetings` - Meeting transcriptions with AI summaries
- `folders` - Knowledge base organization
- `contacts` - Meeting participant management
- `ai_models` - Configurable AI model registry
- `ai_prompts` - Prompt template management
- `meeting_speakers` - Speaker diarization

### AI Processing Pipeline

1. User uploads audio → Aliyun OSS storage
2. Submit to Alibaba Tingwu ASR service
3. Poll task status (async threading in background)
4. LLM processing: classification, keywords, summary generation
5. Save results to database
6. Frontend polls status API for updates

The AI model system is flexible and database-driven:
- Admin can enable/disable models via [Web Admin Portal](backend/static/admin/)
- Runtime model selection by users
- Automatic fallback to rule-based classifier if LLM fails

## Development Commands

### Backend Development

```bash
# Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration (required)
cp .env.example .env
# Edit .env with actual credentials:
# - WeChat AppID/Secret
# - Alibaba Cloud credentials (OSS, Tingwu)
# - AI API keys (OpenAI, Anthropic, Qwen, Doubao)
# - DATABASE_URL for production PostgreSQL

# Run development server
python main.py  # Runs on http://localhost:8000

# API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Frontend Development

WeChat Developer Tools is required:
1. Open WeChat Developer Tools
2. Import project directory: `miniprogram/`
3. Configure AppID in project settings
4. Click "Compile" to preview
5. Use real device for audio recording features (simulator doesn't support wx.startRecord)

### Production Deployment

**IMPORTANT**: Production server uses specific environment:
- Python command: `python3.11` (not `python` or `python3`)
- Virtual environment: `/home/cshine/Cshine/venv` (in project root, NOT backend/)
- Database: PostgreSQL via `DATABASE_URL` env var (parse with urllib.parse.urlparse)
- HTTPS required: `https://cshine.xuyucloud.com` (NOT http IP address)

```bash
# Standard deployment (server-side)
ssh cshine@server
cd /home/cshine/Cshine
git pull origin main
bash docs/deployment/UPDATE_SERVER.sh

# Service management
sudo systemctl restart cshine-api
sudo systemctl status cshine-api
sudo journalctl -u cshine-api -n 50

# Health check
curl http://localhost:8000/health
curl https://cshine.xuyucloud.com/health
```

## Critical Development Rules

### Rule 1: Backend Updates Require Deployment Documentation

**Every time you modify backend code, you MUST create a deployment document:**

```bash
# Use template
cp .github_docs_template.md docs/features/DEPLOY_<功能名>_$(date +%Y%m%d).md

# Fill in all sections:
# - Update type (新功能/Bug修复/性能优化/安全补丁)
# - Priority (必须🔴/建议🟡/可选🟢)
# - Database changes (tables, fields, migration scripts)
# - Dependency changes (requirements.txt)
# - Environment variable changes (.env)
# - Deployment steps (prefer automated: bash docs/deployment/UPDATE_SERVER.sh)
# - Verification methods
# - Rollback plan

# Commit with code
git add .
git commit -m "feat: 新功能 + 线上部署方案

- 实现了 xxx 功能
- 新增了 xxx 接口

部署文档: docs/features/DEPLOY_XXX_$(date +%Y%m%d).md
更新优先级: 建议🟡"
```

**When deployment docs are NOT needed:**
- Frontend-only changes (UI, styles, components)
- Documentation updates
- Comment additions

See [docs/deployment/BACKEND_UPDATE_PROTOCOL.md](docs/deployment/BACKEND_UPDATE_PROTOCOL.md) for full protocol.

### Rule 2: Version Management

Version format: `major.minor.patch` (e.g., `0.9.1`)

**AI assistants must auto-increment patch version on each commit:**
- Current: `0.9.1` → Next commit: `0.9.2`
- Update [docs/core/CHANGELOG.md](docs/core/CHANGELOG.md)
- Include version in commit message: `feat: 新功能 (v0.9.2)`
- Create git tag for significant updates: `git tag v0.9.2`

**DO NOT auto-increment minor/major versions** - requires explicit user approval.

### Rule 3: Resource Reuse Priority

Always check for existing resources before creating new ones:

**Available icons** (in [assets/icons/](assets/icons/)):
- `folder.png`, `add-folder.png`, `add.png`
- `flash-active.png`, `flash.png`
- `knowledge-active.png`, `knowledge.png`
- `profile-active.png`, `profile.png`
- `search.png`, `sort.png`, `menu.png`
- `copy.png`, `delete.png`, `move.png`, `rename.png`, `upfile.png`

**DO NOT** reference non-existent icon paths in code.

### Rule 4: Production Deployment Checklist

When deploying to production, verify:

1. **Code pushed to GitHub** - Confirm latest commit visible in GitHub repo
2. **Server environment** - Use `python3.11`, venv at `/home/cshine/Cshine/venv`
3. **Database config** - Parse `DATABASE_URL` with `urllib.parse.urlparse`
4. **Database migrations** - Initialize `conn = None`, `cursor = None` to avoid UnboundLocalError
5. **Mini Program config** - Production must use HTTPS domain: `https://cshine.xuyucloud.com`
6. **Deployment flow**:
   - Local commit + push
   - Server: pull latest code
   - Run database migrations (if any)
   - Restart service: `sudo systemctl restart cshine-api`
   - Verify: `curl https://cshine.xuyucloud.com/health`
   - Test mini program

See [docs/deployment/LESSONS_LEARNED.md](docs/deployment/LESSONS_LEARNED.md) for detailed lessons.

## API Structure

**Base URL**: `/api/v1/`

**Response format**:
```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

**Authentication**: JWT token in `Authorization: Bearer <token>` header

**Core endpoints**:
- `POST /api/v1/auth/login` - WeChat login (exchange code for token)
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/flash/create` - Create flash recording
- `GET /api/v1/flash/list` - List flash recordings
- `GET /api/v1/flash/{id}/ai-status` - Poll AI processing status
- `POST /api/v1/meeting/create` - Create meeting
- `GET /api/v1/meeting/list` - List meetings
- `GET /api/v1/meeting/{id}` - Get meeting details
- `POST /api/v1/upload/audio` - Upload audio file
- `GET /health` - Health check

## Service Layer Pattern

Backend services are organized by responsibility:

- [backend/app/services/ai_processor.py](backend/app/services/ai_processor.py) - Flash AI processing orchestration
- [backend/app/services/meeting_processor.py](backend/app/services/meeting_processor.py) - Meeting AI pipeline
- [backend/app/services/tingwu_service.py](backend/app/services/tingwu_service.py) - Alibaba Cloud ASR integration
- [backend/app/services/llm_classifier.py](backend/app/services/llm_classifier.py) - LLM-based classification
- [backend/app/services/classifier.py](backend/app/services/classifier.py) - Rule-based fallback classifier
- [backend/app/services/waveform_service.py](backend/app/services/waveform_service.py) - Audio waveform generation

## Documentation Structure

```
docs/
├── core/              # Permanent core documentation (NEVER delete)
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── PRD-完善版.md
│   └── DEVELOPMENT_GUIDE.md
├── deployment/        # Permanent deployment guides (NEVER delete)
│   ├── BACKEND_UPDATE_PROTOCOL.md
│   └── BACKEND_UPDATE_QUICKSTART.md
├── features/          # Temporary deployment docs (3-month lifecycle)
│   └── DEPLOY_*_YYYYMMDD.md
└── archive/           # Archived docs (>3 months old)
```

**Naming convention**: `DEPLOY_<功能名>_<YYYYMMDD>.md`

**Lifecycle**: Features docs auto-archive after 3 months via `docs/cleanup.sh`

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code formatting
- `refactor` - Code refactoring
- `perf` - Performance optimization
- `test` - Tests
- `chore` - Build/tooling

**Examples**:
```bash
feat: 新增会议纪要功能 + 部署文档
fix(auth): 修复 /api/v1/auth/me 接口认证失败问题
docs: 更新后端更新协议和快速上手指南
refactor: 文档结构大重组 - 建立分类管理系统
```

## Testing

**Current state**: Limited formal testing infrastructure

**Manual testing**:
- WeChat Developer Tools for frontend
- Swagger UI at `/docs` for backend API testing
- Production verification: [backend/test_upload_apis.py](backend/test_upload_apis.py)
- Health check: `GET /health`

The project structure supports adding:
- Backend: pytest + pytest-asyncio
- Frontend: WeChat Mini Program test framework

## Key Design Patterns

**Component-based UI**: Reusable WeChat Mini Program components in [miniprogram/components/](miniprogram/components/)

**Service layer**: Business logic separated from API routes

**Database-driven config**: AI models and prompts stored in database, manageable via admin UI

**Async background processing**: Long-running AI tasks run in threads to avoid blocking requests

**JWT authentication**: Token-based auth with 7-day expiry, WeChat OpenID as user identifier

## Common Gotchas

1. **WeChat Mini Program requires HTTPS** in production (no http:// or IP addresses)
2. **Database URL parsing** must use `urllib.parse.urlparse` in production migrations
3. **Python version** on production server is `python3.11` (not `python` or `python3`)
4. **Virtual environment location** is project root `/home/cshine/Cshine/venv` (NOT in backend/)
5. **Audio recording** only works on real devices (not simulator)
6. **Always push to GitHub** before server deployment (server pulls from GitHub)
7. **Initialize cursor variables** (`conn = None`, `cursor = None`) in migration scripts to avoid UnboundLocalError

## Related Documentation

- [README.md](README.md) - Project overview
- [docs/core/CHANGELOG.md](docs/core/CHANGELOG.md) - Version history
- [docs/core/DEVELOPMENT_GUIDE.md](docs/core/DEVELOPMENT_GUIDE.md) - Complete development guide
- [docs/deployment/BACKEND_UPDATE_PROTOCOL.md](docs/deployment/BACKEND_UPDATE_PROTOCOL.md) - Deployment protocol
- [.cursorrules](.cursorrules) - AI assistant rules
- [backend/README.md](backend/README.md) - Backend documentation

## Project Status

**Current version**: v0.9.1

**Completed features**:
- User authentication (WeChat login + JWT)
- Flash recordings (voice → text → AI summary)
- Meeting minutes (upload audio → transcription → structured summary)
- Folder management (knowledge base organization)
- Contact management
- AI model selection (frontend + backend)
- Web admin portal
- Production deployment

**In development**:
- Advanced search (semantic search)
- Data export (Markdown/PDF)
- Tag system enhancements
- Sharing functionality
