import os
import time
import asyncio
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Optional, Dict

import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, status, HTTPException, Request

from . import crud, schemas, models, config, queues
from . import pwd_context, ALGORITHM, oauth2_scheme


HOUR = 3600


def generate_auth_token(user_id: str, expires_delta: timedelta = None):
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=30))

    payload = {
        'public_id': str(user_id),
        'exp': expires
    }
    encoded_token = jwt.encode(payload, config.secret, algorithm=ALGORITHM)

    return encoded_token


async def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.secret, algorithms=[ALGORITHM])
        user_id: str = payload.get("public_id")
        if id is None:
            raise credentials_exception
        else:
            token_data = schemas.TokenData(user_id=user_id)
    except PyJWTError:
        raise credentials_exception

    user = await crud.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    else:
        return user


async def auth_user(username: str, password: str):
    """returns False if not authenticated, else returns the models.User"""
    user = await crud.get_user_by_username(username)
    if user is None:
        return False

    if pwd_context.verify(password, user.hashed_password):
        return user
    else:
        return False


def parse_date(date_: str) -> datetime:
    try:
        return datetime.fromisoformat(date_)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong date format.")


async def clean_db() -> None:
    """Cleans the databases of entries and journals marked as "delete" older than (by default) one week"""
    delete_after_days: int = config.delete_after
    while True:
        week_ago = date.today() - timedelta(days=delete_after_days)

        await models.Journal.filter(deleted_on__lt=week_ago).delete()
        await models.Entry.filter(deleted_on__lt=week_ago).delete()

        await asyncio.sleep(HOUR * 2)


async def clean_backups() -> None:
    """Clean backups older than two weeks old"""
    backups_dir = Path("./mnemeapi/backups")
    backups_dir.mkdir(exist_ok=True)

    two_weeks = HOUR * 24 * 7 * 2

    while True:
        now = int(time.time())
        for item in backups_dir.iterdir():
            if item.suffix != ".db":
                continue

            taken = item.stem
            try:
                taken = int(taken)
            except ValueError:
                continue

            if now - two_weeks > taken:
                os.remove(str(item.resolve()))

        await asyncio.sleep(HOUR * 5)


async def auto_backup() -> None:
    """Create a backup of the database every 24 hours"""
    backups_dir = Path("./mnemeapi/backups")
    backups_dir.mkdir(exist_ok=True)

    while True:
        await crud.backup()
        await asyncio.sleep(HOUR * 24)


async def add_to_queue(user_id: str, event: str, changed_type: str, data: Optional[Dict] = None):
    """
    Add an item to the queue to update the user
        `event` is "edit", "create" or "delete"
        `changed_type` is either "journal" or "entry"
        `data` is the content that got updated or created
    """
    queue = queues.get(user_id)
    if queue is None:
        # The user hasn't subscribe with any device
        return

    update = {
        "event": event,
        "data": {
            "type": changed_type,
            "data": data
        }
    }
    await queue.put(update)


async def updates_generator(user_id: str, request: Request):
    # The user certainly has a queue because it gets created when they subscribe
    queue = queues.get(user_id)
    while True:
        if await request.is_disconnected():
            break

        # No need sleep in the loop because await queue.get() will simply wait until there is something to get
        update = await queue.get()
        yield update
