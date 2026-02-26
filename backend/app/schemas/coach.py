from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import StrUUID


class CoachResponse(BaseModel):
    id: StrUUID
    academy_id: StrUUID | None
    name: str
    email: str
    phone: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CoachLoginResponse(BaseModel):
    token: str
    coach: CoachResponse
