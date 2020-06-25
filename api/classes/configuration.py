from typing import Optional
import configparser

from api.schemas import UserCreate
from api.crud import create_user, get_user_by_username
from api.database import SessionLocal

from . import Singleton


class Configuration(metaclass=Singleton):
    """A configuration singleton to hold things like the secret, if the server is public or not etc"""

    def __init__(self, file: str):
        self.file: str = file
        self._config = configparser.ConfigParser()

        self._secret: Optional[str] = None
        self._public: Optional[bool] = None
        self._host: str = "127.0.0.1"
        self._port: int = 8000
        self._workers: Optional[int] = None

    @property
    def secret(self):
        return self._secret

    @property
    def public(self):
        return self._public

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def workers(self):
        return self._workers

    def load(self):
        """Read and loads the configuration from the file.
            If it is run for a second time while the app is running only the secret
            and if the instance is public or not will change."""
        self._config.read(self.file)

        app = self._config["App"]

        self._host = app.get("host", "127.0.0.1")
        self._port = app.getint("port", fallback=8000)
        self._workers = app.getint("workers", fallback=2)

        self._public = app.getboolean("public", fallback=False)
        secret = app.get("secret")
        if secret is None:
            raise RuntimeError("No secret found")
        else:
            self._secret = secret

    def create_user(self) -> bool:
        """Create the admin user from the config file only if the instance is not public and the user doesn't exists.
           Return True if the user was created, else False"""
        if self.public:
            return False

        db = SessionLocal()

        admin = self._config["Admin User"]
        username = admin.get("username", "admin")
        password = admin.get("password", None)
        if password is None:
            raise RuntimeError("No password found for admin user")

        db_user = get_user_by_username(db, username)
        if db_user is None:
            user = UserCreate(
                encrypted=admin.getboolean("encrypted", fallback=False),
                username=username,
                password=password,
                admin=True
            )
            create_user(db, user)
            db.close()  # pylint: disable=no-member
            return True
        else:
            db.close()  # pylint: disable=no-member
            return False
