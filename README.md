# Serious Backend

A FastAPI backend with JWT authentication, user profiles, and user-owned items.
It uses SQLAlchemy and SQLite by default, includes Alembic migrations, and has
automated tests.

## Run locally on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
py -m uvicorn app.main:app --reload
```

The API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
Explore and try endpoints in the interactive docs at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs); ReDoc is at
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

## API overview

All application routes are under `/api/v1`:

- `POST /auth/register` — create an account
- `POST /auth/login` — exchange username and password for a bearer token
- `GET /users/me` and `PUT /users/me` — read or update the authenticated profile
- `GET /users/{user_id}` — read a user profile
- `/items/` — create, list, read, update, and delete items
- `GET /health` — check backend status

Item creation and listing require authentication. Item updates and deletion are
restricted to the owner or a superuser. The exact request schemas and responses
are documented in Swagger UI.

## Configuration and database

Copy `.env.example` to `.env` and set `SECRET_KEY` to a long, random value before
deploying. The `.env` file and SQLite database files are intentionally excluded
from Git. By default, the app creates `serious_backend.db` in the working
directory. Set `DATABASE_URL` to use another SQLAlchemy database URL.

## Docker

After creating `.env` as described above, run:

```powershell
docker compose up --build
```

## Tests

```powershell
py -m pytest
```
