from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.mcp import MCPClient
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.user_agent import UserAgent
from gocare.agents.unauthorized_agent import UnauthorizedAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "You are GoCare MultiAgent controller. Collect the user's registered mobile, verify via MCP, then hand off to GreetingAgent after success, which immediately transitions to UserAgent. "
    "Never ask for or reveal secrets. Use submit_mobile() when number is provided."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)
        self._mcp = MCPClient()

    async def on_enter(self) -> None:
        self.instructions = BASE_MULTI_INSTRUCTIONS
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Welcome to GoCare. Please say your registered mobile number, including country code."
            )
        )

    @function_tool
    async def submit_mobile(self, context: RunContext, mobile: str) -> tuple[Agent[ConversationContext], str] | str:
        """Verify the user's mobile via MCP and hand off appropriately."""
        ud = self.session.userdata
        digits = re.sub(r"[^\d+]", "", mobile)
        if not digits:
            return "I couldn't detect a number. Please say your full mobile number, including country code."
        ud.user_mobile = digits
        ud.state = SessionState.AUTHENTICATING

        ok, user_id = await self._mcp.authenticate_mobile(digits)
        if ok and user_id:
            ud.is_authenticated = True
            ud.user_id = user_id
            ud.state = SessionState.MAIN
            # greet after auth then proceed to user agent
            return GreetingAgent(), (
                "Thanks. You're verified. Welcome back to GoCare."
            )

        ud.auth_attempts += 1
        if ud.auth_attempts >= 3:
            ud.state = SessionState.UNAUTHORIZED
            return UnauthorizedAgent(), (
                "Verification failed multiple times. Your access is locked."
            )
        return "That number could not be verified. Please try again, including your country code."