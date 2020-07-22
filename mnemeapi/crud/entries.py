from typing import List, Optional
from datetime import datetime, date

from fastapi import HTTPException
from tortoise.query_utils import Q

from .. import schemas
from ..models.models import Entry, Keyword
from . import update_keywords


async def create_entry(entry: schemas.EntryCreate, jrnl_id: int) -> Entry:
    try:
        date_ = datetime.fromisoformat(entry.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Wrong date format.")

    new_entry = Entry(journal_id=jrnl_id, short=entry.short, long=entry.long, date=date_)
    await new_entry.save()
    for kw in entry.keywords:
        await Keyword(entry_id=new_entry.id, word=kw.word.lower()).save()

    await new_entry.fetch_related("keywords")
    return new_entry


async def get_entry_by_id(entry_id: int, deleted: bool = False) -> Optional[Entry]:
    if deleted:
        # Don't care if an entry is marked for deletion
        entry = await Entry.get_or_none(id=entry_id)
    else:
        entry = await Entry.get_or_none(id=entry_id, deleted_on=None)

    if entry is not None:
        await entry.fetch_related("keywords")

    return entry


async def get_entry_by_short(entry_short: str, jrnl_id: int, deleted: bool = False) -> Optional[Entry]:
    if deleted:
        # Don't care if an entry is marked for deletion
        entry = await Entry.get_or_none(short=entry_short, journal_id=jrnl_id)
    else:
        entry = await Entry.get_or_none(short=entry_short, journal_id=jrnl_id, deleted_on=None)

    if entry is not None:
        await entry.fetch_related("keywords")

    return entry


async def delete_entry(entry: Entry, now: Optional[bool] = False) -> None:
    if now:
        await entry.delete()
    else:
        entry.deleted_on = date.today()
        await entry.save()


async def undelete_entry(entry: Entry, new_short: Optional[str] = None) -> Entry:
    entry.deleted_on = None
    if new_short is not None:
        # In case there is a new entry with that short, we need to change this.
        entry.short = new_short

    await entry.save()
    await entry.fetch_related("keywords")
    return entry


async def update_entry(updated_entry: schemas.EntryUpdate, entry_id: int) -> Entry:
    try:
        date_ = datetime.fromisoformat(updated_entry.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Wrong date format.")

    entry = await get_entry_by_id(entry_id)
    entry.journal_id = updated_entry.journal_id
    entry.short = updated_entry.short
    entry.long = updated_entry.long
    entry.date = date_
    await entry.save()

    await update_keywords(updated_entry.keywords, entry_id)

    await entry.fetch_related("keywords")
    return entry


async def get_entries(user_id: int, params, keywords: List[str],
                      date_min: datetime, date_max: datetime,
                      jrnl_id: Optional[int], deleted: bool = False) -> List[Entry]:
    if deleted:
        query = Entry.filter(journal__user_id=user_id)
    else:
        query = Entry.filter(journal__user_id=user_id, deleted_on=None)

    if jrnl_id:
        query = query.filter(journal_id=jrnl_id)
    if date_min:
        query = query.filter(Q(date__gt=date_min))
    if date_max:
        query = query.filter(Q(date__lt=date_max))

    if params.method.lower() == "or":
        query = query.prefetch_related("keywords")
        query = query.filter(Q(keywords__word__in=keywords))
        entries_to_return = await query.all().offset(params.skip).limit(params.limit)
    else:
        entries = await query.all().offset(params.skip).limit(params.limit)
        await Entry.fetch_for_list(entries, "keywords")
        entries_to_return = list()
        for entry in entries:
            words = [w.word.lower() for w in entry.keywords]
            if all(kw.lower() in words for kw in keywords):
                entries_to_return.append(entry)

    return entries_to_return
