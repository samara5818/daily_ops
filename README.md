# Daily Ops Agent

A personal daily-ops planner that generates shift-aware schedules using an LLM, sends reminders, and provides a dashboard to manage plans, schedules, and overrides.

## Features
- JWT auth with SQLite (ready to move to Postgres).
- Planner graph (LLM) with validation and repair.
- Day overrides (per-date shift, goal, diet, appointments, notes).
- Plan history stored per date.
- FastAPI endpoints + lightweight frontend pages.

## Project Layout
- `backend/` FastAPI app, scheduler, planners, DB models
- `frontend/` Static HTML/CSS/JS UI

## Requirements
- Python 3.10+
- `pip`

## Setup

### 1) Create virtualenv
```
python -m venv backend/.venv
backend\.venv\Scripts\activate
```

### 2) Install deps
```
pip install -r backend/requirements.txt
```

### 3) Environment variables
Create `backend/.env` (do not commit this file) with at least:
```
SECRET_KEY=change-me
DATABASE_URL=sqlite:///./daily_ops.db
SMTP_HOST=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
EMAIL_TO=...
```
Optional:
```
ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_ALGORITHM=HS256
FRONTEND_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
PLAN_DAILY_LIMIT=10
```

### 4) Database
Alembic is configured, but **migration versions are ignored** in git for development. If you want migrations, initialize in your local clone.

To create tables directly (dev-only), start the API once; `init_db()` will create tables.

If you want migrations locally:
```
alembic -c backend/alembic.ini revision --autogenerate -m "init"
alembic -c backend/alembic.ini upgrade head
```

### 5) Run the API
```
uvicorn app.main:app --reload --app-dir backend
```

## Frontend
Serve the static UI from a separate terminal:
```
python -m http.server 8001 -d frontend
```

Pages:
- `http://localhost:8001/login.html`
- `http://localhost:8001/profile.html`
- `http://localhost:8001/index.html`

If your backend is not on `http://127.0.0.1:8000`, set in HTML:
```
<script>
  window.API_BASE_URL = "http://127.0.0.1:8000";
</script>
```

## Key Endpoints
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /profile/me`
- `PUT /profile/me`
- `GET /plan/me?now_iso=YYYY-MM-DDTHH:MM:SS`
- `POST /plan-and-schedule/me?now_iso=YYYY-MM-DDTHH:MM:SS`
- `GET /day-overrides/{YYYY-MM-DD}`
- `PUT /day-overrides/{YYYY-MM-DD}`
- `GET /jobs`

## Notes
- `PLAN_DAILY_LIMIT` enforces max plan generations per day (default 10).
- Day overrides are stored per date and injected into planner context.
- Planner history is stored in the `plans` table per date.

## Development Tips
- Delete `backend/daily_ops.db` if schema changes and you want a clean reset.
- Use smaller passwords (bcrypt limit is 72 bytes).
