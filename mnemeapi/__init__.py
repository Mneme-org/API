from typing import Dict
from asyncio import Queue

from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from passlib.context import CryptContext

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from .classes import Configuration  # pylint: disable=wrong-import-position

config = Configuration("config.ini")
config.load()

# user id -> Queue for pushing events to users
queues: Dict[str, Queue] = {}
from .main import app  # pylint: disable=wrong-import-position
