from __future__ import annotations

import re
from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are a session orchestrator. When the user provides a valid mobile number, immediately perform mobile authentication using the available external tool; do not ask for confirmation and do not mention that you are calling a tool. "
    "If authentication succeeds, respond as a verified assistant and proceed to help with account and transaction questions. If it fails 3 times, state that access is locked and provide safe next steps. "
    "For user questions after verification, retrieve any necessary data using the available external tool(s) without exposing tool names or schemas. "
    "Security: Never ask for or reveal secrets (password, PIN, OTP, CVV); refuse such requests politely. "
    "Voice: Keep replies concise and natural. Read phone numbers as digit sequences (E.164 style), not as currency or amounts. Do not output protocol artifacts such as |end|."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Welcome. Please say your registered mobile number, including country code."
            )
        )