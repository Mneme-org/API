from typing import List
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from . import app, security, ACCESS_TOKEN_EXPIRE_MINUTES
from . import crud, models, schemas, utils
from .database import engine

models.Base.metadata.create_all(bind=engine)

@app.get("/login", response_model=schemas.Token)
def login(db: Session = Depends(utils.get_db), credentials: HTTPBasicCredentials = Depends(security)):
    user = utils.auth_user(credentials.username, credentials.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    encoded_token = utils.generate_auth_token(user.public_id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": encoded_token}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(utils.get_db)):
    db_user = crud.get_user_by_username(db, name=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(utils.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users
