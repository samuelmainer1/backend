from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.user import get_user, get_user_by_email, get_user_by_username, update_user
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserOut)
def read_user_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=UserOut)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    if user_in.email and user_in.email != current_user.email:
        if get_user_by_email(db, user_in.email):
            raise HTTPException(status_code=409, detail="Email already registered")
    if user_in.username and user_in.username != current_user.username:
        if get_user_by_username(db, user_in.username):
            raise HTTPException(status_code=409, detail="Username already taken")
    return update_user(db, current_user, user_in)