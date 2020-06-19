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

    assert r.status_code == 201
    assert r.text is not None
    data = r.json()
    assert data["username"] == "test1"
    assert data["journals"] == []
    assert "id" in data
    user_id = data["id"]

    r = client.get(
        "/users/"
    )
    assert r.status_code == 200
    assert r.text is not None
    data = r.json()
    assert user_id in [user["id"] for user in data]


def log_in(username: str, password: str):
    r = client.post(
        "/token",
        data={"username": username, "password": password}
    )
    data = r.json()
    return "Bearer " + data["access_token"]


def create_entries(token: str):
    """Used by test_find_entries"""
    client.post(
        "/journals/journal_1/entries/",
        headers={"Authorization": token},
        json={
            "short": "entry_2",
            "date": "2019-11-03",
            "keywords": [
                {
                    "word": "word1"
                },
                {
                    "word": "word 1"
                },
                {
                    "word": "word 2"
                }
            ]
        }
    )

    client.post(
        "/journals/journal_2/entries/",
        headers={"Authorization": token},
        json={
            "short": "entry_3",
            "date": "2019-11-03",
            "keywords": [
                {
                    "word": "word_1"
                },
                {
                    "word": "word2"
                },
                {
                    "word": "a keyword"
                }
            ]
        }
    )


def test_create_jrnl():
    token = log_in("test1", "12345")

    r = client.post(
        "/journals/",
        headers={"Authorization": token},
        json={
            "name": "journal_1"
        }
    )

    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "journal_1"
    assert data["entries"] == []

    client.post(
        "/journals/",
        headers={"Authorization": token},
        json={
            "name": "journal_2"
        }
    )


def test_read_journals():
    token = log_in("test1", "12345")

    r = client.get(
        "/journals/",
        headers={"Authorization": token},
    )

    assert r.status_code == 200
    data = r.json()
    assert "journal_1" in [jrnl["name"] for jrnl in data]


def test_read_journal():
    token = log_in("test1", "12345")

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
    token = log_in("test1", "12345")

    r = client.post(
        "/journals/journal_1/entries/",
        headers={"Authorization": token},
        json={
            "short": "entry_1",
            "long": "a long text",
            "date": "2010-01-12",
            "keywords": []
        }
    )

    assert r.status_code == 201
    data = r.json()
    assert data["short"] == "entry_1"
    assert data["long"] == "a long text"
    assert data["keywords"] == []


def test_create_entry_with_keyword():
    """Create an entry with keyword"""
    token = log_in("test1", "12345")

    r = client.post(
        "/journals/journal_1/entries/",
        headers={"Authorization": token},
        json={
            "short": "entry_1",
            "date": "2001-10-25",
            "keywords": [{"word": "a keyword"}]
        }
    )

    assert r.status_code == 201
    data = r.json()
    assert data["short"] == "entry_1"
    assert data["keywords"][0]["word"] == "a keyword"
    assert data["id"] == data["keywords"][0]["entry_id"]


# This doesn't test the search function extensively, maybe it should?
def test_find_entries():
    token = log_in("test1", "12345")
    create_entries(token)

    r = client.get(
        "/journals/entries?keywords=a+keyword&limit=100&method=or",
        headers={"Authorization": token}
    )

    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert data[0]["short"] == "entry_1"

    r = client.get(
        "/journals/entries?keywords=word1&keywords=word+1&method=and",
        headers={"Authorization": token}
    )

    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["short"] == "entry_2"

    r = client.get(
        "/journals/entries?keywords=word_1&keywords=a+keyword&method=or",
        headers={"Authorization": token}
    )

    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert data[0]["short"] in ["entry_3", "entry_1"]
    assert data[1]["short"] in ["entry_3", "entry_1"]


def test_update_entry():
    token = log_in("test1", "12345")

    create_entries(token)

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
            "date": "2020-06-19",
            "keywords": [{"word": "an updated keyword"}],
            "jrnl_id": jrnl["id"]
        }
    )

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


def test_delete_entry():
    token = log_in("test1", "12345")

    # Select and delete a random entry
    r = client.get("/journals/", headers={"Authorization": token})
    data = r.json()
    jrnl = random.choice(data)
    entry = random.choice(jrnl["entries"])

    r = client.delete(
        f"/journals/{jrnl['name']}/{entry['id']}",
        headers={"Authorization": token}
    )

    assert r.status_code == 204

    # Check that this entry is the only one that got deleted
    r = client.get("/journals/", headers={"Authorization": token})

    data = r.json()
    new_jrnl = [_jrnl for _jrnl in data if _jrnl['id'] == jrnl['id']][0]

    assert len(new_jrnl['entries']) == len(jrnl['entries']) - 1
    assert [_entry for _entry in new_jrnl['entries'] if _entry['id'] == entry['id']] == []


def test_delete_user():
    r = client.post(
        "/users/",
        json={"username": "test2", "password": "12345"}
    )
    assert r.status_code == 201

    token = log_in("test2", "12345")

    r = client.delete(
        "/users/",
        headers={"Authorization": token}
    )
    assert r.status_code == 204

    r = client.get(
        "/users/"
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert "test2" not in [user['username'] for user in data]
