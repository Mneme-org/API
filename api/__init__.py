from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from passlib.context import CryptContext


security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# TODO Make this actually secret
SECRET_KEY = "839c219801be21b6a1c3ebb054c3c3dexa3c4dfe6e914e10635b2ab39e6ff446"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from .main import app  # pylint: disable=wrong-import-position
