import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player

pytestmark = pytest.mark.asyncio


SEND_URL = "/api/v1/auth/player/otp/send"
VERIFY_URL = "/api/v1/auth/player/otp/verify"
PHONE = "+919876543210"


class TestSendOTP:
    async def test_send_otp_success(self, client: AsyncClient):
        resp = await client.post(SEND_URL, json={"phone": PHONE})

        assert resp.status_code == 200
        assert resp.json() == {"success": True}

    async def test_send_otp_short_phone_rejected(self, client: AsyncClient):
        resp = await client.post(SEND_URL, json={"phone": "123"})

        assert resp.status_code == 422


class TestVerifyOTP:
    async def test_valid_otp_creates_player(self, client: AsyncClient, db_session: AsyncSession):
        """First verify with a new phone auto-creates the player."""
        await client.post(SEND_URL, json={"phone": PHONE})
        resp = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "123456"})

        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["player"]["phone"] == PHONE
        assert data["player"]["skill_level"] == "beginner"
        assert data["player"]["dominant_hand"] == "right"

        # Verify the player was persisted
        result = await db_session.execute(select(Player).where(Player.phone == PHONE))
        player = result.scalar_one()
        assert str(player.id) == data["player"]["id"]

    async def test_valid_otp_returns_existing_player(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Second verify with an existing player returns the same record."""
        existing = Player(name="Rahul", phone=PHONE)
        db_session.add(existing)
        await db_session.commit()
        await db_session.refresh(existing)

        await client.post(SEND_URL, json={"phone": PHONE})
        resp = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "123456"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["player"]["id"] == str(existing.id)
        assert data["player"]["name"] == "Rahul"

    async def test_wrong_otp(self, client: AsyncClient):
        await client.post(SEND_URL, json={"phone": PHONE})
        resp = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "999999"})

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid OTP"

    async def test_expired_otp(self, client: AsyncClient, redis_client):
        """OTP that was never sent (or expired) is rejected."""
        resp = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "123456"})

        assert resp.status_code == 401
        assert resp.json()["detail"] == "OTP expired or not requested"

    async def test_otp_cannot_be_reused(self, client: AsyncClient):
        """After one successful verify, the same OTP is consumed."""
        await client.post(SEND_URL, json={"phone": PHONE})
        resp1 = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "123456"})
        assert resp1.status_code == 200

        resp2 = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "123456"})
        assert resp2.status_code == 401
        assert resp2.json()["detail"] == "OTP expired or not requested"

    async def test_token_is_valid_jwt(self, client: AsyncClient):
        """The returned token can authenticate further requests."""
        await client.post(SEND_URL, json={"phone": PHONE})
        resp = await client.post(VERIFY_URL, json={"phone": PHONE, "otp": "123456"})

        token = resp.json()["token"]

        from app.utils.auth import verify_token

        payload = verify_token(token)
        assert payload["role"] == "player"
        assert payload["user_id"] == resp.json()["player"]["id"]
