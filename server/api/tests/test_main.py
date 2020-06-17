import random

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..database import Base
from ..utils import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()  # pylint: disable=no-member


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_user():
    r = client.post(
        "/users/",
        json={"username": "test1", "password": "12345"}
    )
    print(r.text)
    assert r.status_code == 200
    assert r.text is not None
    data = r.json()
    assert data["username"] == "test1"
    assert data["journals"] == []
    assert "public_id" in data
    user_id = data["public_id"]

    r = client.get(
        "/users/"
    )
    assert r.status_code == 200
    assert r.text is not None
    data = r.json()
    assert user_id in [user["public_id"] for user in data]


def log_in():
    r = client.post(
        "/token",
        data={"username": "test1", "password": "12345"}
    )
    data = r.json()
    return "Bearer " + data["access_token"]


def test_create_jrnl():
    token = log_in()

    r = client.post(
        "/journals/",
        headers={"Authorization": token},
        json={
            "name": "journal_1"
        }
    )
    print(r.text)

    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "journal_1"
    assert data["entries"] == []


def test_read_journals():
    token = log_in()

    r = client.get(
        "/journals/",
        headers={"Authorization": token},
    )

    assert r.status_code == 200
    data = r.json()
    assert "journal_1" in [jrnl["name"] for jrnl in data]


def test_read_journal():
    token = log_in()

    r = client.get(
        "/journals/journal_1",
        headers={"Authorization": token},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "journal_1"
    assert data["entries"] == []


def test_create_entry_with_long():
    """Create an entry with no keywords"""
    token = log_in()

    r = client.post(
        "/journals/journal_1/entries/",
        headers={"Authorization": token},
        json={
            "short": "entry_1",
            "long": "a long text",
            "date": "now",
            "keywords": []
        }
    )

    assert r.status_code == 200
    data = r.json()
    assert data["short"] == "entry_1"
    assert data["long"] == "a long text"
    assert data["date"] == "now"
    assert data["keywords"] == []


def test_create_entry_with_keyword():
    """Create an entry with keyword"""
    token = log_in()

    r = client.post(
        "/journals/journal_1/entries/",
        headers={"Authorization": token},
        json={
            "short": "entry_1",
            "date": "now",
            "keywords": [{"word": "a_keyword"}]
        }
    )

    assert r.status_code == 200
    data = r.json()
    assert data["short"] == "entry_1"
    assert data["date"] == "now"
    assert data["keywords"][0]["word"] == "a_keyword"
    assert data["id"] == data["keywords"][0]["entry_id"]


def test_delete_entry():
    token = log_in()

    # Select and delete a random entry
    r = client.get("/journals/", headers={"Authorization": token})
    data = r.json()
    jrnl = random.choice(data)
    entry = random.choice(jrnl["entries"])

    r = client.delete(
        f"/journals/{jrnl['name']}/{entry['id']}",
        headers={"Authorization": token}
    )

    assert r.status_code == 200

    # Check that this entry is the only one that got deleted
    r = client.get("/journals/", headers={"Authorization": token})

    data = r.json()
    new_jrnl = [_jrnl for _jrnl in data if _jrnl['id'] == jrnl['id']][0]

    assert len(new_jrnl['entries']) == len(jrnl['entries']) - 1
    assert [_entry for _entry in new_jrnl['entries'] if _entry['id'] == entry['id']] == []


def test_update_entry():
    token = log_in()

    # Select and update a random entry
    r = client.get("/journals/", headers={"Authorization": token})
    data = r.json()
    jrnl = random.choice(data)
    entry = random.choice(jrnl["entries"])

    r = client.put(
        f"/journals/{jrnl['name']}/{entry['id']}",
        headers={"Authorization": token},
        json={
            "short": "updated entry",
            "long": "new long",
            "date": "now",
            "keywords": [{"word": "an updated keyword"}],
            "jrnl_id": jrnl["id"]
        }
    )
    print(r.text)
    assert r.status_code == 200
    data = r.json()
    assert data["short"] == "updated entry"
    assert data["long"] == "new long"
    assert data["keywords"][0]["word"] == "an updated keyword"
    assert len(data["keywords"]) == 1

    r = client.get(
        f"/journals/{jrnl['name']}/{data['id']}",
        headers={"Authorization": token}
    )
    assert r.status_code == 200
    new_data = r.json()
    assert new_data == data
