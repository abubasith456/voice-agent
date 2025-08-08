from __future__ import annotations

import re
from typing import Optional

from gocare.agents.base import AgentBase
from gocare.state import ConversationContext, SessionState
from gocare.security import contains_sensitive_request, refusal_message, log_sensitive_attempt

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")


class GreetingAgent(AgentBase):
    def __init__(self) -> None:
        super().__init__(name="greeting")

    async def on_enter(self, ctx: ConversationContext) -> Optional[str]:
        ctx.state = SessionState.GREETING
        return (
            "Welcome to GoCare. To continue, please say your registered mobile number, including country code."
        )

    async def on_user_message(self, text: str, ctx: ConversationContext) -> Optional[str]:
        ctx.last_user_message = text
        if contains_sensitive_request(text):
            log_sensitive_attempt(ctx.user_id, text)
            return refusal_message()

        match = MOBILE_REGEX.search(text)
        if match:
            ctx.user_mobile = re.sub(r"[^\d+]", "", match.group(1))
            ctx.state = SessionState.AUTHENTICATING
            return (
                f"Thanks. I heard {ctx.user_mobile}. Verifying now. If this is incorrect, you can say 'change number'."
            )

        return "Please provide your registered mobile number, including country code."