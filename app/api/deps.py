from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError
from app.crud.user import get_user_by_username
from app.models.user import User
from app.schemas.token import TokenData

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise UnauthorizedError()
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedError()
        token_data = TokenData(username=username)
    except JWTError:
        raise UnauthorizedError()
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise UnauthorizedError()
    return user