from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.user_agent import UserAgent
from gocare.agents.unauthorized_agent import UnauthorizedAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are a session orchestrator. "
    "When the user provides a mobile number, call MCP tool 'authenticate_user' with {mobile_number: <string>}. "
    "If authentication succeeds, include the token [USER_AUTHENTICATED] and then call the function tool 'handoff_to_greeting' with {user_id, name}. "
    "If authentication fails 3 times, include the token [USER_UNAUTHORIZED] and stop. "
    "Security: Never ask for or reveal secrets (password, PIN, OTP, CVV). If asked, refuse. "
    "Voice: Keep replies concise and natural."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.instructions = BASE_MULTI_INSTRUCTIONS
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Welcome. Please say your registered mobile number, including country code."
            )
        )

    @function_tool
    async def handoff_to_greeting(self, context: RunContext, user_id: str, name: str) -> tuple[Agent, str]:
        """Handoff to GreetingAgent after successful authentication."""
        ud = self.session.userdata
        ud.is_authenticated = True
        ud.user_id = user_id
        ud.state = SessionState.MAIN
        return GreetingAgent(), f"Thanks {name}. You're verified."