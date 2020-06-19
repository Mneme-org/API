import uuid
from typing import Optional, List

from sqlalchemy.orm import Session

from .. import schemas
from ..models.models import User
from .. import pwd_context


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, name: str) -> Optional[User]:
    return db.query(User).filter(User.username == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    hashed_password = pwd_context.hash(user.password)

    user_id = str(uuid.uuid4())
    new_user = User(username=user.username, hashed_password=hashed_password, id=user_id)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
