from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.item import create_item, delete_item, get_item, get_items, update_item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item_endpoint(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    return create_item(db, item_in, owner_id=current_user.id)


@router.get("/", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    return get_items(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item_endpoint(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_item(db, item, item_in)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    delete_item(db, item_id)
    return None