import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academy import Academy
from app.models.coach import Coach

LOGIN_URL = "/api/v1/auth/coach/login"
EMAIL = "coach@tsg.com"
PASSWORD = "test1234"


@pytest.fixture
async def seeded_coach(db_session: AsyncSession) -> Coach:
    """Insert an academy and coach for login tests."""
    academy = Academy(name="TSG Bangalore", city="Bangalore")
    db_session.add(academy)
    await db_session.flush()

    coach = Coach(
        academy_id=academy.id,
        name="Coach TSG",
        email=EMAIL,
        password_hash=bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode(),
        phone="+919000000001",
    )
    db_session.add(coach)
    await db_session.commit()
    await db_session.refresh(coach)
    return coach


class TestCoachLogin:
    async def test_valid_login(self, client: AsyncClient, seeded_coach: Coach):
        resp = await client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})

        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["coach"]["email"] == EMAIL
        assert data["coach"]["name"] == "Coach TSG"
        assert data["coach"]["id"] == str(seeded_coach.id)
        assert data["coach"]["is_active"] is True

    async def test_valid_login_returns_valid_jwt(self, client: AsyncClient, seeded_coach: Coach):
        resp = await client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})

        from app.utils.auth import verify_token

        payload = verify_token(resp.json()["token"])
        assert payload["role"] == "coach"
        assert payload["user_id"] == str(seeded_coach.id)

    async def test_wrong_password(self, client: AsyncClient, seeded_coach: Coach):
        resp = await client.post(LOGIN_URL, json={"email": EMAIL, "password": "wrongpass"})

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid password"

    async def test_nonexistent_email(self, client: AsyncClient):
        resp = await client.post(
            LOGIN_URL, json={"email": "nobody@example.com", "password": "whatever"}
        )

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Coach not found"
