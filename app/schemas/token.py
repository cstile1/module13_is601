from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token(BaseModel):
    """Basic token structure used internally."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenData(BaseModel):
    """Payload extracted from JWT."""
    user_id: UUID
    token_type: TokenType
    exp: datetime
    jti: str


class TokenResponse(BaseModel):
    """Full token response returned to the client."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime

    user_id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(
        from_attributes=True
    )
