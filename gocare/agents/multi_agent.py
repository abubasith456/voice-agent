from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.main_agent import MainAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are the session orchestrator. "
    "Flow: (1) Greet and request the registered mobile number. (2) When a valid mobile number appears, immediately call the external tool 'authenticate_user' with {mobile_number: <string>}. "
    "If authentication succeeds, immediately call the external tool 'get_user_info' with {user_id: <string>} to retrieve profile info, including the user's name. "
    "Then call the function tool 'switch_to_main' with {user_id: <string>, name: <string>} to switch to the main assistant. "
    "As main assistant, include the user's name in every spoken response and help with account and transactions. "
    "If authentication fails, politely ask again; after multiple failures, inform that access is locked (but do not mention counts). "
    "Confidentiality: Never ask for or reveal secrets (password, PIN, OTP, CVV); refuse such requests. "
    "Tooling Disclosure: Do not mention tool names, function calls, schemas, or internal processes to the user. "
    "Voice: Keep replies concise and natural. Read phone numbers as digit sequences (E.164 style), not as currency or amounts. Do not output protocol artifacts such as |end|."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Your next message must be exactly: 'Welcome. Please say your registered mobile number, including country code.' Do not add or prepend any other words."
            )
        )

    @function_tool
    async def switch_to_main(self, context: RunContext, user_id: str, name: str) -> tuple[Agent, str]:
        """Switch to MainAgent after successful authentication and profile fetch."""
        ud = self.session.userdata
        ud.user_id = user_id
        ud.user_name = (name or "").strip()
        ud.is_authenticated = True
        ud.state = SessionState.MAIN
        # Return an empty handoff message so only MainAgent.on_enter speaks
        return MainAgent(), ""