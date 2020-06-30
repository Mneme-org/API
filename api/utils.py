import asyncio
from datetime import datetime, timedelta, date

import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, status, HTTPException

from . import crud, schemas, models, config
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
