from typing import List
from datetime import timedelta

from fastapi import FastAPI, Query
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import ACCESS_TOKEN_EXPIRE_MINUTES
from . import models, schemas, crud, config
from .utils import get_db, get_current_user, auth_user, generate_auth_token, parse_date
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
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    encoded_token = generate_auth_token(user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": encoded_token}


@app.post("/users/pub", response_model=schemas.User, status_code=201, name="Create User")
def create_user_pub(*, user: schemas.UserCreate, db: Session = Depends(get_db)):
    """This is the endpoint used if the instance is public so anyone can create an account."""
    if not config.public:
        raise HTTPException(status_code=400, detail="The instance is private.")

    db_user = crud.get_user_by_username(db, name=user.username.lower())
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    else:
        return crud.create_user(db=db, user=user)


@app.post("/users/", response_model=schemas.User, status_code=201, name="Create User")
def create_user(*, user: schemas.UserCreate, db: Session = Depends(get_db),
                cur_user: models.User = Depends(get_current_user)):
    """This is the endpoint used if the instance is private so only an admin can create accounts."""
    if not cur_user.admin:
        raise HTTPException(status_code=403, detail="Only an admin can create new users.")

    db_user = crud.get_user_by_username(db, name=user.username.lower())
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    else:
        return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User], name="Fetch Users")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.delete("/users/", status_code=204)
def delete_user(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the current user and all his data. This is action is irreversible."""
    crud.delete_user(db, user.id)


@app.put("/users/", response_model=schemas.User)
def update_user(*, user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db), new_username: str = None, encrypted: bool = False):
    if new_username is encrypted is None:
        raise HTTPException(status_code=400, detail="New username and encrypted can't be both empty")

    if new_username is not None:
        db_user = crud.get_user_by_username(db, name=new_username.lower())
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        db_user = crud.get_user_by_id(db, user.id)
        return crud.update_user(db, db_user, new_username.lower(), encrypted)
    else:
        db_user = crud.get_user_by_id(db, user.id)
        return crud.update_user(db, db_user, None, encrypted)


@app.post("/users/update_password", status_code=204)
def update_password(*, db: Session = Depends(get_db), user: models.User = Depends(get_current_user),
                    user_password: schemas.UserPassword):
    if auth_user(db, user.username, user_password.current_password):
        if user_password.current_password == user_password.new_password:
            raise HTTPException(status_code=400, detail="New password can't be the same as the old one.")
        else:
            crud.update_user_password(db, user, user_password.new_password)
    else:
        raise HTTPException(status_code=400, detail="Wrong password.")


@app.post('/journals/', response_model=schemas.Journal, status_code=201)
def create_journal(jrnl: schemas.JournalCreate, user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl.name)
    if db_jrnl:
        raise HTTPException(status_code=400, detail="This journal already exists for this user")
    else:
        return crud.create_journal(db, user.id, jrnl)


@app.get("/journals/{jrnl_name}/", response_model=schemas.Journal, name="Fetch Journal")
def read_journal(jrnl_name: str, user: models.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name.lower())
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")
    else:
        return db_jrnl


@app.get("/journals/", response_model=List[schemas.Journal], name="Fetch Journals")
def read_journals(skip: int = 0, limit: int = 100, user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    jrnls = crud.get_journals_for(db, user, skip=skip, limit=limit)
    return jrnls


@app.delete("/journals/{jrnl_name}/", status_code=204)
def delete_journal(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db), jrnl_name: str):
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name.lower())
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    crud.delete_journal(db, db_jrnl)


@app.put("/journals/{jrnl_name}/", response_model=schemas.Journal)
def update_journal(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
                   jrnl_name: str, new_name: str):
    # Check if new_name exists as a journal for the user
    db_jrnl = crud.get_jrnl_by_name(db, user.id, new_name.lower())
    if db_jrnl is not None:
        raise HTTPException(status_code=400, detail="The new journal name already exists for the user")

    # Check jrnl_name belongs to current user
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name.lower())
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    return crud.update_journal(db, db_jrnl, new_name)


@app.post("/journals/{jrnl_name}/entries/", response_model=schemas.Entry, status_code=201)
def create_entry(*, jrnl_name: str, user: models.User = Depends(get_current_user), entry: schemas.EntryCreate,
                 db: Session = Depends(get_db)):
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name.lower())
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    return crud.create_entry(db, entry, db_jrnl.id)


@app.get("/journals/{jrnl_name}/{entry_id}", response_model=schemas.Entry)
def read_entry(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
               jrnl_name: str, entry_id: int):
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name)
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    entry_db = crud.get_entry_by_id(db, entry_id)
    if entry_db is None or entry_db.journal.id != db_jrnl.id:
        raise HTTPException(status_code=404, detail="There is no entry with that id in that journal")
    else:
        return entry_db


@app.delete("/journals/{jrnl_name}/{entry_id}", status_code=204)
def delete_entry(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
                 jrnl_name: str, entry_id: int):
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name)
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
    db_jrnl = crud.get_jrnl_by_name(db, user.id, jrnl_name)
    if db_jrnl is None:
        raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")

    # Check updated_entry.jrnl_id belongs to current user
    if db_jrnl.id != updated_entry.jrnl_id:
        dest_jrnl = crud.get_jrnl_by_id(db, user.id, updated_entry.jrnl_id)
        if dest_jrnl is None:
            raise HTTPException(status_code=404, detail="Destination journal doesn't exists for this user")

    # Check entry_id belongs to current user
    entry_db = crud.get_entry_by_id(db, entry_id)
    if entry_db is None or entry_db.journal.id != db_jrnl.id:
        raise HTTPException(status_code=404, detail="There is no entry with that id in that journal")

    return crud.update_entry(db, updated_entry, entry_id)


@app.get("/journals/entries", response_model=List[schemas.Entry], name="Find entries")
def find_entry(*, user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
               params: schemas.Params = Depends(None), keywords: List[str] = Query(...)):
    """Method parameter is either 'and', or 'or' and it translates to whether it should look for entries
       that have all the keywords, or at least one of them"""
    if params.date_min is None:
        date_min = None
    else:
        date_min = parse_date(params.date_min)
    if params.date_max is None:
        date_max = None
    else:
        date_max = parse_date(params.date_max)

    if params.jrnl_name is not None:
        db_jrnl = crud.get_jrnl_by_name(db, user.id, params.jrnl_name)
        if db_jrnl is None:
            raise HTTPException(status_code=404, detail="This journal doesn't exists for this user")
        else:
            jrnl_id = db_jrnl.id
    else:
        jrnl_id = None

    if params.method in ["or", "and"]:
        # We pass date_min and date_max because now they are datetime objects, not strings
        return crud.get_entries(db, user.id, params, keywords, date_min, date_max, jrnl_id)
    else:
        raise HTTPException(status_code=400, detail="Method parameter can only be 'and' or 'or'.")
