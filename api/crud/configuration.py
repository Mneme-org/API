from typing import Optional
from sqlalchemy.orm import Session
from ..models.models import Configuration


def get_config(db: Session) -> Optional[Configuration]:
    return db.query(Configuration).first()


def create_config(db: Session, secret: str, public: bool):
    new_config = Configuration(secret=secret, public=public)

    db.add(new_config)
    db.commit()
    db.refresh(new_config)


def update_config(db: Session, old_config: Configuration, secret: str, public: bool):
    old_config.secret = secret
    old_config.public = public
    db.commit()


def get_public(db: Session) -> bool:
    config = get_config(db)
    return config.public


def get_secret(db) -> str:
    config = get_config(db)
    return config.secret
