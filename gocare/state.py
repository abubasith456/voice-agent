from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional


class SessionState(Enum):
    GREETING = auto()
    AUTHENTICATING = auto()
    OTP_PENDING = auto()  # New state for OTP verification
    MAIN = auto()
    UNAUTHORIZED = auto()


@dataclass
class ConversationContext:
    state: SessionState = SessionState.GREETING
    user_mobile: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    auth_attempts: int = 0
    last_user_message: Optional[str] = None
    last_agent_message: Optional[str] = None
    is_authenticated: bool = False
    otp_requested: bool = False  # Track if OTP has been requested
    pending_user_id: Optional[str] = None  # Store user_id while waiting for OTP

    def reset_auth(self) -> None:
        self.user_mobile = None
        self.user_id = None
        self.user_name = None
        self.auth_attempts = 0
        self.is_authenticated = False
        self.otp_requested = False
        self.pending_user_id = None
        self.state = SessionState.GREETING