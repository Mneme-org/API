from sqlalchemy.orm import Session
from sqlalchemy import update

from .. import schemas
from ..models.models import Entry, Keyword
from . import update_keywords


def create_entry(db: Session, entry: schemas.EntryCreate, jrnl_id: int) -> Entry:
    new_entry = Entry(jrnl_id=jrnl_id, short=entry.short, long=entry.long, date=entry.date)

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    for kw in entry.keywords:
        new_kw = Keyword(entry_id=new_entry.id, word=kw.word)
        db.add(new_kw)

    db.commit()
    return new_entry


def get_entry_by_id(db: Session, entry_id: int) -> Entry:
    return db.query(Entry).filter(Entry.id == entry_id).first()


def delete_entry(db: Session, entry: Entry) -> None:
    db.delete(entry)
    db.commit()


def update_entry(db: Session, updated_entry: schemas.EntryUpdate, entry_id: int) -> Entry:
    db.query(Entry).filter(Entry.id == entry_id).update({
        "jrnl_id": updated_entry.jrnl_id,
        "short": updated_entry.short,
        "long": updated_entry.long,
        "date": updated_entry.date
    })
    db.commit()
    update_keywords(db, updated_entry.keywords, entry_id)

    return get_entry_by_id(db, entry_id)
