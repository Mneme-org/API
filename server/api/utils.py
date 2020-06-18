from datetime import datetime, timedelta

import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from . import crud, schemas, models
from . import SECRET_KEY, pwd_context, ALGORITHM, oauth2_scheme
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # pylint: disable=no-member


def generate_auth_token(pub_id: str, expires_delta: timedelta = None):
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=30))

    payload = {
        'public_id': pub_id,
        'exp': expires
    }
    encoded_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        public_id: str = payload.get("public_id")
        if public_id is None:
            raise credentials_exception
        else:
            token_data = schemas.TokenData(public_id=public_id)
    except PyJWTError:
        raise credentials_exception

    user = crud.get_user_by_pub_id(db, token_data.public_id)
    if user is None:
        raise credentials_exception
    else:
        return user


def auth_user(db: Session, username: str, password: str):
    """returns False if not authenticated, else returns the models.User"""
    user = crud.get_user_by_username(db, username)
    if user is None:
        return False

    if pwd_context.verify(password, user.hashed_password):
        return user
    else:
        return False


def parse_date(date: str) -> datetime:
    try:
        return datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong date format.")
