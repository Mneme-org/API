import uuid
from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas
from . import pwd_context


def get_user_by_pub_id(db: Session, pub_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.public_id == pub_id).first()


def get_user_by_username(db: Session, name: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.password)

    pub_id = str(uuid.uuid4())
    new_user = models.User(username=user.username, hashed_password=hashed_password, public_id=pub_id)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
