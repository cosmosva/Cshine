# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Cshine** is an AI-powered voice recording and idea management tool built as a WeChat Mini Program with a FastAPI backend.

- **Frontend**: Native WeChat Mini Program (WXML/WXSS/JS)
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Core Features**: Voice recording → AI transcription → Smart summarization → Category management

## Development Commands

### WeChat Mini Program (Frontend)

The mini program has no build step - it runs directly in WeChat Developer Tools:

1. Open WeChat Developer Tools
2. Import project from this directory
3. Click "Compile" to run in simulator
4. Use "Preview" for real device testing (required for recording features)

**Note**: There are no npm scripts or CLI commands for the mini program frontend.

### Backend API

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure environment variables

# Run development server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)

# Code formatting
black app/

# Linting
flake8 app/

# Tests
pytest
```

## Architecture

### Frontend Structure

```
components/          # Reusable components
├── navigation-bar/  # Custom nav bar with safe area support
├── record-button/   # Voice recording with long-press interaction
└── flash-card/      # Display individual flash records

pages/               # Mini program pages
└── index/           # Main page with recording + list view

utils/               # Utility modules
├── request.js       # HTTP request wrapper with auth
├── api.js           # API endpoint definitions
├── storage.js       # localStorage abstraction
├── toast.js         # UI feedback helpers
└── format.js        # Date/time formatting
```

### Key Frontend Patterns

**1. Component-Based Architecture**
- Custom components use WeChat's Component() API
- Components communicate via events (triggerEvent/bind)
- Example: `record-button` triggers `recordend` event with audio data

**2. API Integration Pattern**
- All API calls go through `utils/request.js`
- Automatic token injection from `app.globalData.token`
- Centralized error handling and loading states
- Example:
  ```javascript
  const { post } = require('./utils/request')
  const { API_ENDPOINTS } = require('./utils/config')

  post(API_ENDPOINTS.FLASH_CREATE, {
    title, content, audio_url
  }, { showLoad: true })
  ```

**3. Design System**
- All design tokens in `styles/variables.wxss` as CSS custom properties
- Color scheme: Primary #4A6FE8 (sky blue) → Secondary #7B61FF (purple)
- Spacing: Base unit 8rpx (4px), common values 16rpx/24rpx/32rpx
- Naming: `--color-*`, `--spacing-*`, `--font-size-*`, `--radius-*`

**4. State Management**
- App-level state: `app.js` globalData (token, userInfo, userId)
- Page-level state: Component data() and setData()
- Persistent storage: wx.setStorageSync() via `utils/storage.js`

### Backend Structure

```
app/
├── api/            # API route handlers
│   ├── auth.py     # Login, JWT validation
│   ├── flash.py    # CRUD for flash records
│   └── upload.py   # Audio file upload
├── models.py       # SQLAlchemy ORM models
├── schemas.py      # Pydantic request/response schemas
├── database.py     # DB connection and session
└── utils/
    ├── jwt.py      # JWT token generation/validation
    └── wechat.py   # WeChat API integration
```

**API Response Format**:
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**Authentication**: JWT tokens in `Authorization: Bearer <token>` header, 7-day expiry.

## Critical Implementation Details

### Recording Component (`components/record-button/`)

**Known Issues & Fixes Applied**:

1. **Debounce Protection**: Added check in `onTouchStart()` to prevent double-trigger
   ```javascript
   if (this.data.isRecording) return  // Already recording
   ```

2. **Cancel Logic**: Uses `isCancelled` flag to distinguish cancel from normal stop
   - When user slides up >60px, sets `isCancelled = true`
   - In `onStop` callback, checks flag before processing audio

3. **Permission Handling**: Currently relies on error catching
   - **TODO**: Add proactive `wx.authorize({ scope: 'scope.record' })` check
   - **TODO**: Guide users to settings if permission denied

4. **Wave Animation Positioning**: Waves are inside `.record-button` to follow transform
   - Parent uses `overflow: visible` to allow waves to extend beyond button
   - Uses `will-change: transform` for performance

**Recording Flow**:
1. Long press → `onTouchStart()` → Initialize RecorderManager
2. Recording → Timer updates display every 100ms
3. Slide up >60px → Enter cancel state (visual feedback)
4. Release:
   - If cancelled: `onStop` ignored, trigger `recordcancel` event
   - If normal: Process audio, check min duration (1s), trigger `recordend` event

**Min Duration**: Currently 0.3s for testing, should be 1s in production.

### Style System Architecture

**Three-Layer Approach**:
1. `styles/variables.wxss`: Design tokens (colors, spacing, etc.)
2. `styles/common.wxss`: Utility classes and resets
3. Component/page styles: Use variables, avoid magic numbers

**Important**:
- Global `.container` class was removed (had problematic 200rpx padding)
- Page element has `margin: 0; padding: 0` reset in `app.wxss`
- Avoid duplicate `.page` definitions (handled by global styles)

### AI Processing Pattern

**Current Flow** (as implemented):
1. Upload audio → Backend returns `task_id`
2. Frontend polls `/api/v1/flash/{task_id}/status` every 2s
3. When `status === 'completed'`, fetch full result
4. Timer cleanup in `app.globalData.aiPollingTimers`

**Polling Implementation**:
```javascript
// Store timer for cleanup
const app = getApp()
app.globalData.aiPollingTimers[taskId] = setInterval(async () => {
  const status = await checkAIStatus(taskId)
  if (status.completed) {
    clearInterval(app.globalData.aiPollingTimers[taskId])
    delete app.globalData.aiPollingTimers[taskId]
    // Update UI
  }
}, 2000)
```

## Development Conventions

### Naming

- **Files**: kebab-case (`record-button.js`, `flash-card.wxml`)
- **Components**: PascalCase in usage (`<record-button />`)
- **Variables**: camelCase (`flashList`, `isRecording`)
- **CSS Classes**: kebab-case (`.flash-card`, `.record-section`)

### Git Commits

Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `style:` Code formatting (no logic change)
- `refactor:` Code restructuring
- `test:` Test additions/updates
- `chore:` Build/tooling changes

### Component Development

When creating new components:
1. Place in `components/` with folder matching component name
2. Include 4 files: `.wxml`, `.wxss`, `.js`, `.json`
3. Use `Component()` API, not `Page()`
4. Expose events for parent communication, not direct data binding
5. Add `pointer-events: none` to decorative children to avoid blocking touch events

## Common Pitfalls

1. **Recording doesn't work in simulator**: Recording requires real device testing
2. **Left sidebar whitespace**: Check for `margin`/`padding` on page containers
3. **Waves not following button**: Ensure wave container is child of button, not sibling
4. **API calls fail**: Verify token in `app.globalData.token` and backend is running
5. **Transform animations conflict**: Multiple transforms need to be combined in one property
6. **RecorderManager listeners**: Global singleton, listeners persist - handle in `detached()` lifecycle

## Backend API Essentials

### Key Endpoints

```
POST   /api/v1/auth/login         # WeChat login (no auth)
GET    /api/v1/auth/me            # Get current user
POST   /api/v1/flash/create       # Create flash record
GET    /api/v1/flash/list         # List with filters
GET    /api/v1/flash/{id}         # Get detail
PUT    /api/v1/flash/{id}         # Update
DELETE /api/v1/flash/{id}         # Delete
PUT    /api/v1/flash/{id}/favorite # Toggle favorite
POST   /api/v1/upload/audio       # Upload audio file
```

### Database Models

**User**: `id`, `openid`, `nickname`, `avatar`, `subscription_tier`
**Flash**: `id`, `user_id`, `title`, `content`, `summary`, `keywords` (JSONB), `category`, `audio_url`, `is_favorite`
**Meeting**: (future) Similar to Flash with additional fields for participants and action items

### Environment Config

Required in backend `.env`:
- `DATABASE_URL`: PostgreSQL connection (SQLite for dev)
- `SECRET_KEY`: JWT signing key
- `WECHAT_APP_ID` / `WECHAT_APP_SECRET`: WeChat auth
- Optional: ASR/LLM API keys when integrating AI services

## What's Not Implemented Yet

- Backend ASR (Automatic Speech Recognition) integration
- Backend LLM integration for summaries
- Meeting transcription feature
- Search functionality
- Detail page editing
- User settings page

These are marked as TODOs in the codebase and PRD documents.
