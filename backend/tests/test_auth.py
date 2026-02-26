from datetime import UTC, datetime, timedelta

import pytest
from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient
from jose import jwt

from app.config import settings
from app.utils.auth import (
    ALGORITHM,
    create_access_token,
    get_current_user,
    require_role,
    verify_token,
)

# ---------------------------------------------------------------------------
# Test app with protected endpoints
# ---------------------------------------------------------------------------

app = FastAPI()


@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/coach-only")
async def coach_only_route(current_user: dict = Depends(require_role("coach"))):
    return current_user


client = TestClient(app)


# ---------------------------------------------------------------------------
# create_access_token / verify_token
# ---------------------------------------------------------------------------


class TestCreateAccessToken:
    def test_returns_valid_jwt(self):
        token = create_access_token("user-123", "player")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])

        assert payload["sub"] == "user-123"
        assert payload["role"] == "player"
        assert "exp" in payload

    def test_token_has_correct_expiry(self):
        token = create_access_token("user-123", "coach")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])

        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        expected = datetime.now(UTC) + timedelta(minutes=settings.jwt_expiry_minutes)

        # Allow 5 seconds of drift
        assert abs((exp - expected).total_seconds()) < 5

    def test_different_roles(self):
        for role in ("player", "coach", "admin"):
            token = create_access_token("u1", role)
            result = verify_token(token)
            assert result["role"] == role


class TestVerifyToken:
    def test_valid_token(self):
        token = create_access_token("user-456", "coach")
        result = verify_token(token)

        assert result == {"user_id": "user-456", "role": "coach"}

    def test_expired_token(self):
        payload = {
            "sub": "user-789",
            "role": "player",
            "exp": datetime.now(UTC) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)

        with pytest.raises(Exception) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_signature(self):
        token = jwt.encode(
            {"sub": "user-1", "role": "player", "exp": datetime.now(UTC) + timedelta(hours=1)},
            "wrong-secret",
            algorithm=ALGORITHM,
        )

        with pytest.raises(Exception) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_token(self):
        with pytest.raises(Exception) as exc_info:
            verify_token("not.a.jwt")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_sub_claim(self):
        payload = {
            "role": "player",
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)

        with pytest.raises(Exception) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_role_claim(self):
        payload = {
            "sub": "user-1",
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)

        with pytest.raises(Exception) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# get_current_user dependency (via test client)
# ---------------------------------------------------------------------------


class TestGetCurrentUser:
    def test_valid_token(self):
        token = create_access_token("user-100", "player")
        resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json() == {"user_id": "user-100", "role": "player"}

    def test_missing_header(self):
        resp = client.get("/protected")

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self):
        resp = client.get("/protected", headers={"Authorization": "Bearer garbage"})

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token(self):
        payload = {
            "sub": "user-1",
            "role": "player",
            "exp": datetime.now(UTC) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)
        resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# require_role dependency
# ---------------------------------------------------------------------------


class TestRequireRole:
    def test_correct_role_allowed(self):
        token = create_access_token("coach-1", "coach")
        resp = client.get("/coach-only", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json() == {"user_id": "coach-1", "role": "coach"}

    def test_wrong_role_forbidden(self):
        token = create_access_token("player-1", "player")
        resp = client.get("/coach-only", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_no_token_unauthorized(self):
        resp = client.get("/coach-only")

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
