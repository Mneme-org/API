from typing import Optional

from .. import schemas
from ..models import Journal, User, Entry


async def get_journals_for(user: User, skip: int = 0, limit: int = 100):
    jrnls = await Journal.filter(user_id=user.id).offset(skip).limit(limit).all()
    await Journal.fetch_for_list(jrnls, "entries")
    for jrnl in jrnls:
        await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return jrnls


async def get_jrnl_by_name(user_id: str, jrnl_name: str) -> Optional[Journal]:
    jrnl = await Journal.filter(name_lower=jrnl_name, user_id=user_id).get_or_none()
    if jrnl is not None:
        await jrnl.fetch_related("entries")
        await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return jrnl


async def get_jrnl_by_id(user_id: str, jrnl_id: int) -> Optional[Journal]:
    return await Journal.get_or_none(user_id=user_id, id=jrnl_id)


async def create_journal(user_id: str, jrnl: schemas.JournalCreate) -> Journal:
    name = jrnl.name
    new_jrnl = Journal(user_id=user_id, name=name, name_lower=name.lower())
    await new_jrnl.save()

    await new_jrnl.fetch_related("entries")
    await Entry.fetch_for_list(list(new_jrnl.entries), "keywords")

    return new_jrnl


async def delete_journal(db_journal: Journal):
    await db_journal.delete()


async def update_journal(db_journal: Journal, new_name: str) -> Journal:
    db_journal.name = new_name
    db_journal.name_lower = new_name.lower()
    await db_journal.save()
    return db_journal
