import os

TEST_DB_PATH = os.path.abspath("test_backend.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import app.core.database as database_module  # noqa: E402
from app.main import app  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.api.deps import get_db  # noqa: E402

engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Point the app's database module at the test engine so init_db / get_db use the test DB
database_module.engine = engine
database_module.SessionLocal = TestingSessionLocal

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def get_test_client():
    return TestClient(app)