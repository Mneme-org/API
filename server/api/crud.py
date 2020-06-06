import uuid
from typing import Optional

from sqlalchemy.orm import Session

from . import schemas
from .models import User, Journal
from . import pwd_context


def get_user_by_pub_id(db: Session, pub_id: str) -> Optional[User]:
    return db.query(User).filter(User.public_id == pub_id).first()


def get_user_by_username(db: Session, name: str) -> Optional[User]:
    return db.query(User).filter(User.username == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    hashed_password = pwd_context.hash(user.password)

    pub_id = str(uuid.uuid4())
    new_user = User(username=user.username, hashed_password=hashed_password, public_id=pub_id)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_jrnl_by_name(db: Session, pub_user_id: str, jrnl_name: str) -> Optional[Journal]:
    return db.query(Journal).filter(Journal.name == jrnl_name, pub_user_id == pub_user_id).first()


def create_journal(db: Session, pub_user_id: str, jrnl: schemas.JournalCreate) -> Journal:
    name = jrnl.name
    new_jrnl = Journal(pub_user_id=pub_user_id, name=name)

    db.add(new_jrnl)
    db.commit()
    db.refresh(new_jrnl)

    return new_jrnl


def get_journals_for(db: Session, user: User, skip: int = 0, limit: int = 100):
    return db.query(Journal).filter(Journal.pub_user_id == user.public_id).offset(skip).limit(limit).all()
