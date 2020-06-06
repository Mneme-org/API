from sqlalchemy.orm import Session

from server.api import schemas
from server.api.models.models import Entry, Keyword


def create_entry(db: Session, entry: schemas.EntryCreate) -> Entry:
    new_entry = Entry(jrnl_id=entry.jrnl_id, short=entry.short, long=entry.long, date=entry.date)

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    for kw in entry.keywords:
        new_kw = Keyword(entry_id=new_entry.id, word=kw.word)
        db.add(new_kw)
        db.commit()
        db.refresh(new_kw)

    return new_entry
