# Launchpad API

A demo backend built with FastAPI and SQLite. It includes a health check, CRUD
APIs for items, notes, and tasks, and interactive API documentation.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore and try
the API. Alternative documentation is available at
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

## Endpoints

- `GET /health` — check that the backend is running
- `POST /items` — create an item (`name`, `description`)
- `GET /items` — list items
- `GET /items/{item_id}` — get an item
- `PUT /items/{item_id}` — replace an item's fields
- `DELETE /items/{item_id}` — delete an item
- `POST /notes` — create a note (`title`, `content`)
- `GET /notes` — list notes
- `GET /notes/{note_id}` — get a note
- `PUT /notes/{note_id}` — replace a note's fields
- `DELETE /notes/{note_id}` — delete a note
- `POST /tasks` — create a task (`title`, `description`, `completed`)
- `GET /tasks` — list tasks
- `GET /tasks/{task_id}` — get a task
- `PUT /tasks/{task_id}` — replace a task's fields
- `DELETE /tasks/{task_id}` — delete a task

Create and update requests are validated. Missing records return `404 Not Found`;
successful deletes return `204 No Content`.

The SQLite database is created as `backend.db` in the current working
directory. Set the `DATABASE_PATH` environment variable to choose another file.