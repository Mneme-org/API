import sys
from datetime import datetime, timedelta
import configparser
from dataclasses import dataclass

import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from . import crud, schemas, models
from . import pwd_context, ALGORITHM, oauth2_scheme
from .database import SessionLocal


@dataclass()
class Config:
    secret: str
    public: bool


config = Config("", False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # pylint: disable=no-member


def generate_auth_token(user_id: str, expires_delta: timedelta = None):
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=30))

    payload = {
        'public_id': user_id,
        'exp': expires
    }
    encoded_token = jwt.encode(payload, config.secret, algorithm=ALGORITHM)

    return encoded_token


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
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

    user = crud.get_user_by_id(db, token_data.user_id)
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


def read_config() -> (str, int, int):
    """It returns the host, port, and workers for the server"""
    config_parser = configparser.ConfigParser()
    config_parser.read("config.ini")

    app = config_parser["App"]

    public = app.getboolean("public")
    secret = app.get("secret")

    db = SessionLocal()

    if not public:
        admin = config_parser["Admin User"]
        username = admin.get("username")

        # Create the admin user if he doesn't exists
        db_user = crud.get_user_by_username(db, username)
        if db_user is None:
            user = schemas.UserCreate(
                encrypted=admin.getboolean("encrypted"),
                username=username,
                password=admin.get("password"),
                admin=True
            )
            crud.create_user(db, user)

    db_config = crud.get_config(db)

    if db_config is None:
        crud.create_config(db, secret, public)
    else:
        if db_config.public != public:
            old = "public" if db_config.public else "private"
            new = "public" if public else "private"
            answer = input(f"You are about to change this instance from {old} to {new}, are you sure? ")
            if answer.lower() not in ["yes", "y"]:
                sys.exit(0)

            crud.update_config(db, db_config, db_config.secret, public)
        if db_config.secret != secret:
            answer = input("You are about to change the secret, are you sure? ")
            if answer.lower() not in ["yes", "y"]:
                sys.exit(0)

            crud.update_config(db, db_config, secret, db_config.public)

    config.secret = secret
    config.public = public
    return app.get("host", "127.0.0.1"), app.getint("port") or 8000, app.getint("workers") or 2
