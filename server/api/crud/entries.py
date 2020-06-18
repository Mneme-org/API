from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from ..utils import parse_date
from .. import schemas
from ..models.models import Entry, Keyword, Journal
from . import update_keywords


def create_entry(db: Session, entry: schemas.EntryCreate, jrnl_id: int) -> Entry:
    date = parse_date(entry.date)
    new_entry = Entry(jrnl_id=jrnl_id, short=entry.short, long=entry.long, date=date)

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
    date = parse_date(updated_entry.date)
    db.query(Entry).filter(Entry.id == entry_id).update({
        "jrnl_id": updated_entry.jrnl_id,
        "short": updated_entry.short,
        "long": updated_entry.long,
        "date": date
    })
    db.commit()
    update_keywords(db, updated_entry.keywords, entry_id)

    return get_entry_by_id(db, entry_id)


def get_entries(db: Session, user_id: str, params, keywords: List[str],
                date_min: datetime, date_max: datetime, jrnl_id: Optional[int]) -> List[Entry]:
    query = db.query(Entry).join(Entry.keywords).join(Entry.journal)\
        .filter(Journal.pub_user_id == user_id)
    if jrnl_id:
        query = query.filter(Entry.jrnl_id == jrnl_id)
    if date_min:
        query = query.filter(Entry.date > date_min)
    if date_max:
        query = query.filter(Entry.date < date_max)

    if params.method.lower() == "or":
        query = query.filter(Keyword.word.in_(keywords))
        entries_to_return = query.offset(params.skip).limit(params.limit).all()
    else:
        entries = query.offset(params.skip).limit(params.limit).all()
        entries_to_return = list()
        for entry in entries:
            words = [w.word.lower() for w in entry.keywords]
            if all(kw.lower() in words for kw in keywords):
                entries_to_return.append(entry)

    return entries_to_return
