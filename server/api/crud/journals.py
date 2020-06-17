from typing import Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..models import Journal, User


def get_journals_for(db: Session, user: User, skip: int = 0, limit: int = 100):
    return db.query(Journal).filter(Journal.pub_user_id == user.public_id).offset(skip).limit(limit).all()


def get_jrnl_by_name(db: Session, pub_user_id: str, jrnl_name: str) -> Optional[Journal]:
    return db.query(Journal).filter(Journal.name_lower == jrnl_name, Journal.pub_user_id == pub_user_id).first()


def get_jrnl_by_id(db: Session, pub_user_id: str, jrnl_id: int) -> Optional[Journal]:
    return db.query(Journal).filter(Journal.id == jrnl_id, Journal.pub_user_id == pub_user_id).first()


def create_journal(db: Session, pub_user_id: str, jrnl: schemas.JournalCreate) -> Journal:
    name = jrnl.name
    new_jrnl = Journal(pub_user_id=pub_user_id, name=name, name_lower=name.lower())

    db.add(new_jrnl)
    db.commit()
    db.refresh(new_jrnl)

    return new_jrnl
