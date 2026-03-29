# Krishi Officer

AI-powered crop advisory and pest detection platform built for Indian farming workflows.

Live URL: https://krishi-officer.onrender.com

![Krishi Officer Logo](static/assets/Logo.png)

## Product Preview

![Landing Page](static/assets/260327_02h48m27s_screenshot.png)
![Dashboard](static/assets/260327_02h48m57s_screenshot.png)
![Crop Advisory](static/assets/260327_02h49m16s_screenshot.png)
![Pest Detection](static/assets/260327_02h49m27s_screenshot.png)

## Purpose

Krishi Officer helps farmers get fast, practical, organic-first guidance by combining image analysis and conversational follow-up.

It is designed to:
- Detect likely pest or disease patterns from crop images
- Provide crop health advisory when pests are not visible
- Support iterative follow-up in the same session instead of one-off answers
- Preserve session history so users can revisit past diagnostics

## Product Objectives

- Improve first-response accuracy for crop/pest issues through a structured AI output contract
- Keep advice actionable within 24-48 hours, with low-cost, local, organic approaches
- Reduce repeat user effort through persistent chat sessions and message history
- Serve multilingual users with UI and response language support

## Current Capabilities

- Secure signup/login with Supabase Auth
- Protected routes with Bearer token validation middleware
- AI analysis endpoint for image + text or text-only guidance
- Follow-up continuity logic (intent detection, role lock, anti-repeat guard)
- Session lifecycle APIs (create/list/view/delete)
- PostgreSQL persistence for sessions and messages
- Responsive web UI for landing, dashboard, pest detection, and crop advisory
- Language options in UI: English, Hindi, Marathi, Tamil, Telugu
- Official Docker support for local run and container-based deployment

## Tech Stack

### Backend

- Python 3.11 (Render runtime)
- Flask 3.1.1
- Gunicorn 23.0.0
- python-dotenv 1.0.1

### AI and Imaging

- Google Gemini via google-generativeai 0.8.5
- Pillow 11.2.1

### Data and Auth

- Supabase Python SDK 2.15.3 (Auth + table API usage)
- PostgreSQL
- psycopg2-binary 2.9.10 (connection pool + SQL execution)

### Frontend

- Server-rendered HTML templates
- Vanilla JavaScript modules
- Custom CSS (dashboard, chat, auth, landing)

### Deployment

- Render Web Service
- Procfile process: gunicorn app:app
- Docker image support via Dockerfile and .Dockerignore

## Architecture Overview

Krishi Officer follows a monolithic Flask architecture with server-rendered pages and JSON APIs.

Flow summary:
1. User signs in and gets a Supabase access token.
2. Frontend sends protected API requests with Authorization: Bearer token.
3. Flask middleware validates token using Supabase Auth and injects authenticated user into request context.
4. Analyze route composes prompt context, calls Gemini, validates JSON response structure, formats advisory text, and stores messages.
5. Session/message APIs query PostgreSQL-backed tables for history rendering.

## Repository Map

```text
krishi-officer/
|- app.py
|- supabase_client.py
|- database/
|  |- db.py
|  |- schema.sql
|- middleware/
|  |- auth_middleware.py
|- routes/
|  |- analyze_routes.py
|  |- session_routes.py
|  |- message_routes.py
|- services/
|  |- gemini_service.py
|  |- prompt_registry.py
|- static/
|  |- css/
|  |- js/
|  |- assets/
|- templates/
|  |- index.html
|  |- dashboard.html
|  |- crop-advisory.html
|  |- pest-detection.html
|  |- login.html
|  |- signup.html
|- tests/
|  |- verify_auth.py
|- requirements.txt
|- runtime.txt
|- Procfile
|- Dockerfile
|- .Dockerignore
```

## API Surface

### Public page routes

- GET /
- GET /dashboard
- GET /pest-detection
- GET /crop-advisory
- GET /login
- GET /signup

### Auth routes

- POST /signup
- POST /login

### Protected chat routes

- POST /analyze-crop
- POST /sessions
- GET /sessions
- GET /sessions/<session_id>/messages
- DELETE /sessions/<session_id>

### Additional protected routes

- POST /create-chat
- POST /send-message

## Database Model

Schema is initialized at app startup from database/schema.sql.

Tables:
- ai_sessions
  - id UUID primary key (gen_random_uuid())
  - user_id UUID
  - created_at timestamp
- ai_messages
  - id serial primary key
  - session_id UUID references ai_sessions(id) on delete cascade
  - role check in (user, model)
  - content text
  - created_at timestamp

Indexes:
- idx_ai_sessions_user_created_at
- idx_ai_messages_session_created_at

## UI Walkthrough (Live Product)

Based on the current deployment at https://krishi-officer.onrender.com:

- Landing page introduces two primary tools: Pest Detection and Crop Advisory
- Dashboard shows aggregate session stats and shortcuts for new analyses
- Crop Advisory page supports image attachment, typed query, and session history replay
- Pest Detection page mirrors advisory flow with dedicated diagnosis context

## Local Development Setup

### 1. Clone

```bash
git clone <your-repo-url>
cd krishi-officer
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create .env in project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
DATABASE_URL=postgresql://user:password@host:port/postgres?sslmode=require
SECRET_KEY=your_flask_secret
FLASK_DEBUG=true
```

Notes:
- Do not wrap env values in quotes on Render.
- For Supabase pooler connections, include sslmode=require in DATABASE_URL.

### 5. Run the app

```bash
python app.py
```

App runs on http://localhost:5000 by default.

## Render Deployment Notes

- Build installs dependencies from requirements.txt
- Start command is defined in Procfile as gunicorn app:app
- Runtime is pinned via runtime.txt

Recommended Render environment variables:
- GEMINI_API_KEY
- SUPABASE_URL
- SUPABASE_KEY
- DATABASE_URL
- SECRET_KEY

## Docker Support (Official)

Docker is now an official part of this project.

Supported workflow:
- Build image from the project Dockerfile
- Run container locally with .env
- Push image to Docker Hub
- Deploy the same container image on cloud platforms

## Testing

Basic auth flow tests are available:

```bash
python -m unittest tests/verify_auth.py
```

## Security and Operations

- Never commit .env or secrets to git
- Rotate credentials immediately if exposed
- Use strong SUPABASE_KEY and SECRET_KEY values
- Enforce TLS/SSL for database connections in production

## Known Improvement Areas

- Separate dedicated API endpoints for crop vs pest analysis modes (currently both pages post to /analyze-crop)
- Expand automated testing for route-level and frontend integration coverage
- Add observability around AI failures, retries, and latency metrics
- Add role-based auth and stronger server-side validation hardening


