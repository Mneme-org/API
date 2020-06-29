from typing import Optional, List

from .. import schemas
from ..models.models import User, Entry, Journal
from .. import pwd_context


async def get_user_by_id(user_id: str) -> Optional[User]:
    user = await User.get_or_none(id=user_id)
    if user is not None:
        await user.fetch_related("journals")
        await Journal.fetch_for_list(list(user.journals), "entries")
        for jrnl in user.journals:
            await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return user


async def get_user_by_username(name: str) -> Optional[User]:
    user = await User.get_or_none(username=name)
    if user is not None:
        await user.fetch_related("journals")
        await Journal.fetch_for_list(list(user.journals), "entries")
        for jrnl in user.journals:
            await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return user


async def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    users = await User.all().offset(skip).limit(limit)
    await User.fetch_for_list(users, "journals")
    for user in users:
        await Journal.fetch_for_list(list(user.journals), "entries")
        for jrnl in user.journals:
            await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return users


async def create_user(user: schemas.UserCreate) -> User:
    hashed_password = pwd_context.hash(user.password)

    username = user.username.lower()
    new_user = await User.create(
        username=username,
        hashed_password=hashed_password,
        encrypted=user.encrypted,
        admin=user.admin
    )

    await new_user.fetch_related("journals")
    for jrnl in new_user.journals:
        await Journal.fetch_for_list(list(new_user.journals), "entries")
        await Entry.fetch_for_list(list(jrnl.entries), "keywords")

    return new_user


async def delete_user(user_id: str):
    await User.filter(id=user_id).delete()


async def update_user(db_user: User, new_username: Optional[str], encrypted: Optional[bool]) -> User:
    if new_username is not None:
        db_user.username = new_username
    if encrypted is not None:
        db_user.encrypted = encrypted

    await db_user.save()
    return db_user


async def update_user_password(db_user: User, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    db_user.hashed_password = hashed_password

    await db_user.save()
