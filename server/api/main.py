from typing import List
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import app, security, ACCESS_TOKEN_EXPIRE_MINUTES
from . import crud, models, schemas, utils
from .database import engine

models.Base.metadata.create_all(bind=engine)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(utils.get_db)):
    user = utils.auth_user(db, form_data.username, form_data.password)

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
    else:
        return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(utils.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post('/journals/', response_model=schemas.Journal)
def create_journal(jrnl: schemas.JournalCreate, user: models.User = Depends(utils.get_current_user),
                   db: Session = Depends(utils.get_db)):
    db_jrnl = crud.get_jrnl(db, user.public_id, jrnl)
    if db_jrnl:
        raise HTTPException(status_code=400, detail="This journal already exists for this user")
    else:
        return crud.create_journal(db, user.public_id, jrnl)


@app.get("/journals/", response_model=List[schemas.Journal])
def read_journals(skip: int = 0, limit: int = 100, user: models.User = Depends(utils.get_current_user),
                  db: Session = Depends(utils.get_db)):
    jrnls = crud.get_journals_for(db, user, skip=skip, limit=limit)
    return jrnls