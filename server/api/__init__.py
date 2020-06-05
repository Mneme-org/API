from fastapi import FastAPI
from fastapi.security import HTTPBasic
from passlib.context import CryptContext

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# TODO Make this actually secret
SECRET_KEY = "839c219801be21b6a1c3ebb054c3c3dexa3c4dfe6e914e10635b2ab39e6ff446"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30