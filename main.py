import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field


DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "backend.db"))
RESOURCE_COLUMNS = {
    "items": {"name": "TEXT NOT NULL", "description": "TEXT NOT NULL DEFAULT ''"},
    "notes": {"title": "TEXT NOT NULL", "content": "TEXT NOT NULL DEFAULT ''"},
    "tasks": {
        "title": "TEXT NOT NULL",
        "description": "TEXT NOT NULL DEFAULT ''",
        "completed": "INTEGER NOT NULL DEFAULT 0",
    },
}
RESOURCE_LABELS = {"items": "Item", "notes": "Note", "tasks": "Task"}


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as connection:
        for table, columns in RESOURCE_COLUMNS.items():
            definitions = ", ".join(
                f"{column} {definition}" for column, definition in columns.items()
            )
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table} "
                f"(id INTEGER PRIMARY KEY AUTOINCREMENT, {definitions})"
            )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Launchpad API",
    description="A starter REST API with SQLite storage for items, notes, and tasks.",
    version="1.0.0",
    lifespan=lifespan,
)


class ItemInput(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    description: Annotated[str, Field(max_length=1000)] = ""


class Item(ItemInput):
    id: int


class NoteInput(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=120)]
    content: Annotated[str, Field(max_length=5000)] = ""


class Note(NoteInput):
    id: int


class TaskInput(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=120)]
    description: Annotated[str, Field(max_length=1000)] = ""
    completed: bool = False


class Task(TaskInput):
    id: int


def create_record(table: str, values: dict[str, object]) -> dict[str, object]:
    columns = list(values)
    placeholders = ", ".join("?" for _ in columns)
    with connect() as connection:
        cursor = connection.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            tuple(values[column] for column in columns),
        )
        row = connection.execute(
            f"SELECT * FROM {table} WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return dict(row)


def list_records(table: str) -> list[dict[str, object]]:
    with connect() as connection:
        rows = connection.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def get_record(table: str, record_id: int) -> dict[str, object]:
    with connect() as connection:
        row = connection.execute(
            f"SELECT * FROM {table} WHERE id = ?", (record_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{RESOURCE_LABELS[table]} not found",
        )
    return dict(row)


def update_record(
    table: str, record_id: int, values: dict[str, object]
) -> dict[str, object]:
    columns = list(values)
    assignments = ", ".join(f"{column} = ?" for column in columns)
    with connect() as connection:
        cursor = connection.execute(
            f"UPDATE {table} SET {assignments} WHERE id = ?",
            (*[values[column] for column in columns], record_id),
        )
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{RESOURCE_LABELS[table]} not found",
        )
    return get_record(table, record_id)


def delete_record(table: str, record_id: int) -> None:
    with connect() as connection:
        cursor = connection.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{RESOURCE_LABELS[table]} not found",
        )


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["items"]
)
def create_item(item: ItemInput) -> Item:
    return Item(**create_record("items", item.model_dump()))


@app.get("/items", response_model=list[Item], tags=["items"])
def list_items() -> list[Item]:
    return [Item(**row) for row in list_records("items")]


@app.get("/items/{item_id}", response_model=Item, tags=["items"])
def get_item(item_id: int) -> Item:
    return Item(**get_record("items", item_id))


@app.put("/items/{item_id}", response_model=Item, tags=["items"])
def update_item(item_id: int, item: ItemInput) -> Item:
    return Item(**update_record("items", item_id, item.model_dump()))


@app.delete(
    "/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["items"]
)
def delete_item(item_id: int) -> Response:
    delete_record("items", item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/notes", response_model=Note, status_code=status.HTTP_201_CREATED, tags=["notes"]
)
def create_note(note: NoteInput) -> Note:
    return Note(**create_record("notes", note.model_dump()))


@app.get("/notes", response_model=list[Note], tags=["notes"])
def list_notes() -> list[Note]:
    return [Note(**row) for row in list_records("notes")]


@app.get("/notes/{note_id}", response_model=Note, tags=["notes"])
def get_note(note_id: int) -> Note:
    return Note(**get_record("notes", note_id))


@app.put("/notes/{note_id}", response_model=Note, tags=["notes"])
def update_note(note_id: int, note: NoteInput) -> Note:
    return Note(**update_record("notes", note_id, note.model_dump()))


@app.delete(
    "/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"]
)
def delete_note(note_id: int) -> Response:
    delete_record("notes", note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["tasks"]
)
def create_task(task: TaskInput) -> Task:
    return Task(**create_record("tasks", task.model_dump()))


@app.get("/tasks", response_model=list[Task], tags=["tasks"])
def list_tasks() -> list[Task]:
    return [Task(**row) for row in list_records("tasks")]


@app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: int) -> Task:
    return Task(**get_record("tasks", task_id))


@app.put("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def update_task(task_id: int, task: TaskInput) -> Task:
    return Task(**update_record("tasks", task_id, task.model_dump()))


@app.delete(
    "/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"]
)
def delete_task(task_id: int) -> Response:
    delete_record("tasks", task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
