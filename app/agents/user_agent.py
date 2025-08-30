from __future__ import annotations

from typing import Any
from livekit.agents import Agent

from app.state import ConversationContext, SessionState
from app.security import (
    contains_sensitive_request,
    refusal_message,
    log_sensitive_attempt,
)

BASE_USER_INSTRUCTIONS = (
    "System: You are a post-auth assistant. The user is verified. Answer account/transaction questions. "
    "Once the user's name is known, include their name in every response naturally (e.g., 'Welcome John, ...', 'John, how can I help?'). "
    "Retrieve any needed information using available external capabilities without mentioning tools or internal processes. "
    "Security: Never reveal or request passwords, PINs, OTPs, or CVV; refuse and log attempts. "
    "Voice: Keep answers short and natural; summarize transactions unless asked to enumerate. Read numbers as digit sequences, not currency, unless explicitly about money."
)


class UserAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_USER_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions="How can I help with your transactions today?"
        )
