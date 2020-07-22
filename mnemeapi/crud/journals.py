from datetime import date
from typing import Optional

from tortoise.query_utils import Prefetch

from . import delete_entry, undelete_entry
from .. import schemas
from ..models import Journal, User, Entry


async def get_journals_for(user: User, skip: int = 0, limit: int = 100, deleted: bool = False):
    if deleted:
        jrnls = await Journal.filter(user_id=user.id).offset(skip).limit(limit).all()
    else:
        jrnls = await Journal.all()\
            .prefetch_related(Prefetch("entries", queryset=Entry.filter(deleted_on=None)))\
            .filter(user_id=user.id, deleted_on=None).offset(skip).limit(limit).all()

    await Journal.fetch_for_list(jrnls, "entries")
    for jrnl in jrnls:
        await Entry.fetch_for_list(list(jrnl.entries), "keywords")
        if not deleted:
            await jrnl.filter(deleted_on=None)

    return jrnls


async def get_jrnl_by_name(user_id: str, jrnl_name: str, deleted: bool = False) -> Optional[Journal]:
    if deleted:
        jrnl = await Journal.get_or_none(name_lower=jrnl_name, user_id=user_id)
        if jrnl is not None:
            await jrnl.fetch_related("entries__keywords")
    else:
        jrnl = await Journal.all()\
            .prefetch_related(Prefetch("entries", queryset=Entry.filter(deleted_on=None)))\
            .get_or_none(name_lower=jrnl_name, user_id=user_id, deleted_on=None)
        if jrnl is not None:
            await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return jrnl


async def get_jrnl_by_id(user_id: str, jrnl_id: int, deleted: bool = False) -> Optional[Journal]:
    if deleted:
        jrnl = await Journal.get_or_none(user_id=user_id, id=jrnl_id)
    else:
        jrnl = await Journal.get_or_none(user_id=user_id, id=jrnl_id, deleted_on=None)

    if jrnl is not None:
        await jrnl.fetch_related("entries__keywords")
        if not deleted:
            await jrnl.entries.filter(deleted_on=None)

    return jrnl


async def create_journal(user_id: str, jrnl: schemas.JournalCreate) -> Journal:
    name = jrnl.name
    new_jrnl = Journal(user_id=user_id, name=name, name_lower=name.lower())
    await new_jrnl.save()

    await new_jrnl.fetch_related("entries__keywords")

    return new_jrnl


async def delete_journal(db_journal: Journal, now: Optional[bool] = False):
    if now:
        await db_journal.delete()
    else:
        db_journal.deleted_on = date.today()
        for entry in db_journal.entries:
            await delete_entry(entry, now=now)

        await db_journal.save()


async def undelete_journal(db_journal: Journal, new_name: Optional[str] = None) -> Journal:
    db_journal.deleted_on = None
    if new_name is not None:
        # In case there is a new journal with that name we need to update it
        await update_journal(db_journal, new_name)

    await db_journal.fetch_related("entries__keywords")
    await db_journal.save()
    for entry in db_journal.entries:
        await undelete_entry(entry)

    return db_journal


async def update_journal(db_journal: Journal, new_name: str) -> Journal:
    db_journal.name = new_name
    db_journal.name_lower = new_name.lower()
    await db_journal.save()
    return db_journal
