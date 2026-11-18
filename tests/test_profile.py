import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from server.services.profile import DEMO_USER_ID

EMPTY_PROFILE = {
    "basics": {"name": None, "headline": None},
    "education": [],
    "experience": [],
    "projects": [],
    "skills": [],
    "stories": [],
}

PROFILE = {
    "basics": {"name": "Ada Lovelace", "headline": "Analytical engineer"},
    "education": [
        {"school": "University of London", "degree": "BSc", "year": "1835", "details": None},
        {"school": "Trinity College", "degree": "MA", "year": "1840", "details": "Mathematics"},
    ],
    "experience": [
        {"company": "Analytical Engine Co", "role": "Engineer", "period": "1842-1843", "details": "Notes"},
        {"company": "Royal Society", "role": "Fellow", "period": "1844-1850", "details": None},
    ],
    "projects": [
        {"name": "Bernoulli program", "tech": "Analytical Engine", "details": None},
        {"name": "Note G", "tech": None, "details": "First published algorithm"},
    ],
    "skills": ["Algorithms", "Mathematics"],
    "stories": [
        {"title": "Notes on the Analytical Engine", "content": "Published 1843"},
        {"title": "Bernoulli numbers", "content": None},
    ],
}


def test_fresh_database_returns_empty_profile(client: TestClient) -> None:
    response = client.get("/profile")

    assert response.status_code == 200
    assert response.json() == EMPTY_PROFILE


def test_put_then_get_round_trips_in_order(client: TestClient) -> None:
    put_response = client.put("/profile", json=PROFILE)
    get_response = client.get("/profile")

    assert put_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json() == PROFILE
    assert put_response.json() == get_response.json()


def test_put_without_projects_saves_empty_projects(client: TestClient) -> None:
    client.put("/profile", json=PROFILE)
    without_projects = {key: value for key, value in PROFILE.items() if key != "projects"}

    put_response = client.put("/profile", json=without_projects)

    assert put_response.status_code == 200
    assert client.get("/profile").json() == {**PROFILE, "projects": []}


@pytest.mark.parametrize(
    ("body", "field"),
    [
        pytest.param({"skills": "python"}, "skills", id="skills-is-a-string"),
        pytest.param({"skills": [""]}, "skills", id="empty-skill"),
        pytest.param({"skills": ["  "]}, "skills", id="whitespace-only-skill"),
        pytest.param({"projects": None}, "projects", id="null-list"),
    ],
)
def test_invalid_put_is_rejected_and_keeps_previous_profile(client: TestClient, body: dict, field: str) -> None:
    client.put("/profile", json=PROFILE)

    response = client.put("/profile", json=body)

    assert response.status_code == 422
    assert any(field in error["loc"] for error in response.json()["detail"])
    assert client.get("/profile").json() == PROFILE


def test_malformed_json_is_rejected_and_keeps_previous_profile(client: TestClient) -> None:
    client.put("/profile", json=PROFILE)

    response = client.put(
        "/profile",
        content=b'{"skills": ["python"',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "body"
    assert client.get("/profile").json() == PROFILE


def test_repeated_calls_keep_one_demo_user_and_profile(client: TestClient, engine: Engine) -> None:
    for _ in range(5):
        client.get("/profile")
        client.put("/profile", json=PROFILE)

    with engine.connect() as connection:
        user_ids = connection.execute(text("SELECT id::text FROM users")).scalars().all()
        profile_count = connection.execute(text("SELECT count(*) FROM profiles")).scalar_one()

    assert user_ids == [str(DEMO_USER_ID)]
    assert profile_count == 1


def test_unknown_fields_are_dropped(client: TestClient, engine: Engine) -> None:
    body = {
        "basics": {"name": "Ada", "photo_url": "https://example.com/ada.png"},
        "education": [{"school": "University of London", "gpa": "4.0"}],
        "hobbies": ["chess"],
    }
    expected = {
        **EMPTY_PROFILE,
        "basics": {"name": "Ada", "headline": None},
        "education": [{"school": "University of London", "degree": None, "year": None, "details": None}],
    }

    put_response = client.put("/profile", json=body)

    assert put_response.json() == expected
    assert client.get("/profile").json() == expected
    with engine.connect() as connection:
        stored = connection.execute(text("SELECT document FROM profiles")).scalar_one()
    assert stored == expected
