import random
import asyncio

from fastapi.testclient import TestClient
import pytest
from tortoise.contrib.test import finalizer, initializer

from api import app
from api.crud import create_user
from api.schemas import UserCreate

loop = asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
def init_db(request):
    db_url = "sqlite://:memory:"
    initializer(
        ["api.models.models"],
        db_url=db_url
    )
    # Create the admin user since it's a private instance
    admin = UserCreate(username="admin", admin=True, encrypted=False, password="12345")
    loop.run_until_complete(create_user(admin))

    request.addfinalizer(finalizer)


client = TestClient(app)


def log_in(username: str, password: str):
    r = client.post(
        "/login",
        data={"username": username, "password": password}
    )

    data = r.json()
    return "Bearer " + data["access_token"]


def test_create_user():
    r = client.post(
        "/users/",
        json={"username": "test1", "password": "12345", "encrypted": True}
    )
    assert r.status_code == 401

    # It's a private instance so we should authenticate
    token = log_in("admin", "12345")

    r = client.post(
        "/users/",
        json={"username": "test1", "password": "12345", "encrypted": True},
        headers={"Authorization": token},
    )

    assert r.status_code == 201
    assert r.text is not None
    data = r.json()
    assert data["username"] == "test1"
    assert data["encrypted"] is True
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
            "short": "entry",
            "long": "a long text",
            "date": "2010-01-12",
            "keywords": []
        }
    )

    assert r.status_code == 201
    data = r.json()
    assert data["short"] == "entry"
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
    assert data[0]["id"] in [2, 4]
    assert data[1]["id"] in [2, 4]

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
    assert len(data) == 3
    assert data[0]["short"] in ["entry_1", "entry_3"]
    assert data[1]["short"] in ["entry_1", "entry_3"]


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
            "journal_id": jrnl["id"]
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
        f"/journals/{jrnl['name']}/{entry['id']}?now=true",
        headers={"Authorization": token}
    )

    assert r.status_code == 204

    # Check that this entry is the only one that got deleted
    r = client.get("/journals/", headers={"Authorization": token})

    data = r.json()
    new_jrnl = [_jrnl for _jrnl in data if _jrnl['id'] == jrnl['id']][0]

    assert len(new_jrnl['entries']) == len(jrnl['entries']) - 1
    assert [_entry for _entry in new_jrnl['entries'] if _entry['id'] == entry['id']] == []


def test_update_journal():
    token = log_in("test1", "12345")
    r = client.put(
        "/journals/journal_1/?new_name=some+name",
        headers={"Authorization": token}
    )

    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "some name"

    r = client.get(
        "/journals/some%20name/",
        headers={"Authorization": token}
    )
    assert r.status_code == 200

    r = client.get(
        "/journals/journal_1/",
        headers={"Authorization": token}
    )
    assert r.status_code == 404


def test_delete_journal():
    token = log_in("test1", "12345")
    r = client.delete(
        "/journals/some%20name/?now=true",
        headers={"Authorization": token}
    )
    assert r.status_code == 204

    r = client.get(
        "/journals/some+name",
        headers={"Authorization": token}
    )
    assert r.status_code == 404


def test_update_user():
    token = log_in("test1", "12345")
    r = client.put(
        "/users/?new_username=new_username&encrypted=0",
        headers={"Authorization": token},
    )

    assert r.status_code == 200
    data = r.json()
    assert data['username'] == "new_username"
    assert data['encrypted'] is False

    r = client.get("/users/")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    user_names = [user['username'] for user in data]
    assert "new_username" in user_names
    assert "test1" not in user_names


def test_update_user_password():
    token = log_in("new_username", "12345")

    r = client.post(
        "/users/update_password",
        headers={"Authorization": token},
        json={
            "current_password": "12345",
            "new_password": "54321"
        }
    )

    assert r.status_code == 204

    r = client.post(
        "/login",
        data={"username": "new_username", "password": "12345"}
    )
    assert r.status_code == 401
    r = client.post(
        "/login",
        data={"username": "new_username", "password": "54321"}
    )
    assert r.status_code == 200


def test_delete_user():
    token = log_in("admin", "12345")
    r = client.post(
        "/users/",
        json={"username": "test2", "password": "12345"},
        headers={"Authorization": token}
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
    assert len(data) == 2
    assert "test2" not in [user['username'] for user in data]
