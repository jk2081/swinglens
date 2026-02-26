import random
import string

import bcrypt
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.coach import Coach
from app.models.player import Player
from app.schemas.auth import CoachLoginRequest, OTPSendRequest, OTPSendResponse, OTPVerifyRequest
from app.schemas.coach import CoachLoginResponse, CoachResponse
from app.schemas.player import PlayerOTPVerifyResponse, PlayerResponse
from app.utils.auth import create_access_token
from app.utils.exceptions import AuthError, NotFoundError

router = APIRouter(prefix="/auth", tags=["auth"])

OTP_TTL_SECONDS = 300  # 5 minutes
DEV_OTP = "123456"


def _redis_otp_key(phone: str) -> str:
    return f"otp:{phone}"


async def get_redis() -> aioredis.Redis:
    """Yield an async Redis connection."""
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()


async def get_db() -> AsyncSession:
    """Yield an async database session."""
    async with async_session() as session:
        yield session


@router.post("/player/otp/send", response_model=OTPSendResponse)
async def send_otp(
    body: OTPSendRequest,
    r: aioredis.Redis = Depends(get_redis),
) -> OTPSendResponse:
    """Send a one-time password to the player's phone number."""
    if settings.app_env == "development":
        otp = DEV_OTP
    else:
        otp = "".join(random.choices(string.digits, k=6))
        # TODO: send OTP via SMS provider (MSG91, etc.)

    await r.set(_redis_otp_key(body.phone), otp, ex=OTP_TTL_SECONDS)
    return OTPSendResponse(success=True)


@router.post("/player/otp/verify", response_model=PlayerOTPVerifyResponse)
async def verify_otp(
    body: OTPVerifyRequest,
    r: aioredis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> PlayerOTPVerifyResponse:
    """Verify the OTP and return a JWT + player record.

    Auto-creates the player if they don't exist yet.
    """
    key = _redis_otp_key(body.phone)
    stored_otp = await r.get(key)

    if stored_otp is None:
        raise AuthError("OTP expired or not requested")

    if stored_otp != body.otp:
        raise AuthError("Invalid OTP")

    # OTP is valid — delete it so it can't be reused
    await r.delete(key)

    # Look up or auto-create the player
    result = await db.execute(select(Player).where(Player.phone == body.phone))
    player = result.scalar_one_or_none()

    if player is None:
        player = Player(name="", phone=body.phone)
        db.add(player)
        await db.commit()
        await db.refresh(player)

    token = create_access_token(str(player.id), "player")

    return PlayerOTPVerifyResponse(
        token=token,
        player=PlayerResponse.model_validate(player),
    )


@router.post("/coach/login", response_model=CoachLoginResponse)
async def coach_login(
    body: CoachLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> CoachLoginResponse:
    """Authenticate a coach with email and password."""
    result = await db.execute(select(Coach).where(Coach.email == body.email))
    coach = result.scalar_one_or_none()

    if coach is None:
        raise NotFoundError("Coach not found")

    if not bcrypt.checkpw(body.password.encode(), coach.password_hash.encode()):
        raise AuthError("Invalid password")

    token = create_access_token(str(coach.id), "coach")

    return CoachLoginResponse(
        token=token,
        coach=CoachResponse.model_validate(coach),
    )
