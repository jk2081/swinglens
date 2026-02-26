from fastapi import HTTPException, status


class AuthError(HTTPException):
    """Authentication failure — bad credentials, expired OTP, etc."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class NotFoundError(HTTPException):
    """Resource not found."""

    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(HTTPException):
    """Request validation failure beyond what Pydantic catches."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class ForbiddenError(HTTPException):
    """User lacks permission for the action."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class StorageError(HTTPException):
    """S3 / object storage failure."""

    def __init__(self, detail: str = "Storage error"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


class PoseEstimationError(HTTPException):
    """MediaPipe pose estimation failure."""

    def __init__(self, detail: str = "Pose estimation failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
