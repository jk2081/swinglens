from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import StrUUID


class PlayerResponse(BaseModel):
    id: StrUUID
    academy_id: StrUUID | None
    coach_id: StrUUID | None
    name: str
    phone: str
    handicap: Decimal | None
    skill_level: str
    dominant_hand: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerOTPVerifyResponse(BaseModel):
    token: str
    player: PlayerResponse
