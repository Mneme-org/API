from typing import List
from datetime import timedelta

from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import ACCESS_TOKEN_EXPIRE_MINUTES
from . import models, schemas, crud
from .utils import get_db, get_current_user, auth_user, generate_auth_token
from .database import engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mneme",
    description="A self-hosted multi-platform journal keeping app"
)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    encoded_token = generate_auth_token(user.public_id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": encoded_token}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, name=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    else:
        return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post('/journals/', response_model=schemas.Journal)
def create_journal(jrnl: schemas.JournalCreate, user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    db_jrnl = crud.get_jrnl_by_name(db, user.public_id, jrnl.name.lower())
    if db_jrnl:
        raise HTTPException(status_code=400, detail="This journal already exists for this user")
    else:
        return crud.create_journal(db, user.public_id, jrnl)


@app.get("/journals/{jrnl_name}/", response_model=schemas.Journal)
def read_journal(jrnl_name: str, user: models.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    db_jrnl = crud.get_jrnl_by_name(db, user.public_id, jrnl_name.lower())
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")
    else:
        return db_jrnl


@app.get("/journals/", response_model=List[schemas.Journal])
def read_journals(skip: int = 0, limit: int = 100, user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    jrnls = crud.get_journals_for(db, user, skip=skip, limit=limit)
    return jrnls


@app.post("/journals/{jrnl_name}/entries/", response_model=schemas.Entry)
def create_entry(*, jrnl_name: str, user: models.User = Depends(get_current_user), entry: schemas.EntryCreate,
                 db: Session = Depends(get_db)):
    db_jrnl = crud.get_jrnl_by_name(db, user.public_id, jrnl_name.lower())
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    return crud.create_entry(db, entry, db_jrnl.id)


@app.get("/journals/{jrnl_name}/{entry_id}", response_model=schemas.Entry)
def read_entry(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
               jrnl_name: str, entry_id: int):
    db_jrnl = crud.get_jrnl_by_name(db, user.public_id, jrnl_name)
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    entry_db = crud.get_entry_by_id(db, entry_id)
    if entry_db is None or entry_db.journal.id != db_jrnl.id:
        raise HTTPException(status_code=404, detail="There is no entry with that id in that journal")
    else:
        return entry_db


@app.delete("/journals/{jrnl_name}/{entry_id}")
def delete_entry(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
                 jrnl_name: str, entry_id: int):
    db_jrnl = crud.get_jrnl_by_name(db, user.public_id, jrnl_name)
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    entry_db = crud.get_entry_by_id(db, entry_id)
    if entry_db is None or entry_db.journal.id != db_jrnl.id:
        raise HTTPException(status_code=404, detail="There is no entry with that id in that journal")

    crud.delete_entry(db, entry_db)


@app.put("/journals/{jrnl_name}/{entry_id}", response_model=schemas.Entry)
def update_entry(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
                 jrnl_name: str, entry_id: int, updated_entry: schemas.EntryUpdate):
    # Check jrnl_name belongs to current user
    db_jrnl = crud.get_jrnl_by_name(db, user.public_id, jrnl_name)
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    # Check updated_entry.jrnl_id belongs to current user
    if db_jrnl.id != updated_entry.jrnl_id:
        dest_jrnl = crud.get_jrnl_by_id(db, user.public_id, updated_entry.jrnl_id)
        if dest_jrnl is None:
            raise HTTPException(status_code=404, detail="Destination journal doesn't exists for this user")

    # Check entry_id belongs to current user
    entry_db = crud.get_entry_by_id(db, entry_id)
    if entry_db is None or entry_db.journal.id != db_jrnl.id:
        raise HTTPException(status_code=404, detail="There is no entry with that id in that journal")

    return crud.update_entry(db, updated_entry, entry_id)
