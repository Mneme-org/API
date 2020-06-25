from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from passlib.context import CryptContext

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from .classes import Configuration  # pylint: disable=wrong-import-position

config = Configuration("config.ini")
config.load()

from .main import app  # pylint: disable=wrong-import-position

config.create_user()
