# Playto KYC Pipeline

A production-ready full-stack KYC onboarding pipeline for fintech, featuring strict state machine enforcement, secure file validation, role-based authorization, queue + SLA logic, and clean API design.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 4.2 + Django REST Framework |
| Frontend | React 18 + Vite + Tailwind CSS 3 |
| Database | PostgreSQL (default) / SQLite (fallback) |
| Auth | Token-based (DRF TokenAuthentication) |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) PostgreSQL 14+

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed test data
python seed.py

# Run tests
python manage.py test tests

# Start server
python manage.py runserver
```

Backend runs at: `http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

### 3. Login

Use seed credentials:

| Role | Email | Password |
|------|-------|----------|
| Merchant | merchant1@example.com | merchant123 |
| Merchant | merchant2@example.com | merchant123 |
| Reviewer | reviewer@example.com | reviewer123 |

## Environment Variables

### Backend (`backend/`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | dev key | Django secret key |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated hosts |
| `DB_ENGINE` | `sqlite` | `sqlite` or `postgresql` |
| `DB_NAME` | `kyc_pipeline` | Database name (PostgreSQL) |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `postgres` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated CORS origins |

### PostgreSQL Setup (Optional)

```bash
# Set environment variables
set DB_ENGINE=postgresql
set DB_NAME=kyc_pipeline
set DB_USER=postgres
set DB_PASSWORD=yourpassword

# Then run migrations
python manage.py migrate
```

## API Endpoints

All under `/api/v1/`:

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register/` | None | Register user |
| POST | `/auth/login/` | None | Login, get token |
| GET | `/auth/me/` | Any | Current user info |
| GET | `/merchant/submissions/` | Merchant | List own submissions |
| POST | `/merchant/submissions/` | Merchant | Create draft |
| PUT | `/merchant/submissions/:id/` | Merchant | Update draft |
| POST | `/merchant/submissions/:id/submit/` | Merchant | Submit draft |
| POST | `/merchant/submissions/:id/resubmit/` | Merchant | Resubmit |
| GET/POST | `/merchant/submissions/:id/documents/` | Merchant | List/upload docs |
| GET | `/reviewer/queue/` | Reviewer | Queue + stats |
| GET | `/reviewer/submissions/:id/` | Reviewer | View any submission |
| POST | `/reviewer/submissions/:id/pick/` | Reviewer | Pick up |
| POST | `/reviewer/submissions/:id/approve/` | Reviewer | Approve |
| POST | `/reviewer/submissions/:id/reject/` | Reviewer | Reject |
| POST | `/reviewer/submissions/:id/request-info/` | Reviewer | Request info |
| GET | `/notifications/` | Merchant | List notifications |

## Project Structure

```
playto-kyc-pipeline/
├── backend/
│   ├── config/          # Django settings, URLs, WSGI, exception handler
│   ├── users/           # User model, auth views, permissions
│   ├── kyc/             # KYC models, views, serializers
│   │   └── services/    # State machine, file validator, SLA, queue, notifications
│   ├── notifications/   # Notification model, views
│   ├── tests/           # State machine tests
│   └── seed.py          # Test data seeder
├── frontend/
│   └── src/
│       ├── api/         # Axios client
│       ├── context/     # Auth context
│       ├── components/  # Shared UI components
│       └── pages/       # Route pages
├── README.md
└── EXPLAINER.md
```
