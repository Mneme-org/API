from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from passlib.context import CryptContext


security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# TODO Make this actually secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from .main import app  # pylint: disable=wrong-import-position
