from pydantic import BaseModel, Field


class OTPSendRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)


class OTPSendResponse(BaseModel):
    success: bool


class OTPVerifyRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    otp: str = Field(..., min_length=6, max_length=6)


class CoachLoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
