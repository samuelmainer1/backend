from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def get_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()


def create_item(db: Session, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item(**item_in.model_dump(), owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    data = item_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_item, field, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> None:
    db_item = get_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()