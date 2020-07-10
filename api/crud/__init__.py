import time
from pathlib import Path

import aiosqlite
from tortoise import Tortoise

from .keywords import update_keywords
from .entries import create_entry, get_entry_by_id, delete_entry, update_entry, get_entries, undelete_entry, \
    get_entry_by_short
from .journals import get_jrnl_by_id, get_jrnl_by_name, get_journals_for, create_journal, delete_journal, \
    update_journal, undelete_journal
from .users import get_user_by_id, get_user_by_username, get_users, create_user, delete_user, update_user, \
    update_user_password


async def backup() -> None:
    """Backup the database"""
    backups_dir = Path("./api/backups")
    backups_dir.mkdir(exist_ok=True)

    now = int(time.time())
    client = Tortoise.get_connection("default")

    async with aiosqlite.connect(f"./api/backups/{now}.db") as dest:
        async with client.acquire_connection() as conn:
            await conn.backup(target=dest, pages=5)
