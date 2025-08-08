from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.user_agent import UserAgent
from gocare.agents.unauthorized_agent import UnauthorizedAgent
from gocare.mcp import MCPClient

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are a session orchestrator. When the user provides a mobile number, immediately verify it without asking for confirmation. "
    "Call the authenticate_user tool with the detected number. Do not mention tool names, internal functions, schemas, or that you are calling a tool. "
    "If authentication succeeds, proceed to greeting and then main assistance. If authentication fails 3 times, stop and indicate that access is locked. "
    "Security: Never ask for or reveal secrets (password, PIN, OTP, CVV). If asked, refuse. "
    "Voice: Keep replies concise and natural. Read phone numbers as digit sequences (E.164 style), never as currency or amounts. Do not output artifacts like |end|."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)
        self._mcp = MCPClient()

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Welcome. Please say your registered mobile number, including country code."
            )
        )

    @function_tool
    async def authenticate_user(self, context: RunContext, mobile_number: str) -> tuple[Agent, str] | str:
        """Verify the user's mobile number via MCP and hand off appropriately."""
        ud = self.session.userdata
        # Keep only digits and leading plus
        digits = re.sub(r"[^\d+]", "", mobile_number)
        if not digits:
            return "I couldn't detect a number. Please say your full mobile number, including country code."
        ud.user_mobile = digits
        ud.state = SessionState.AUTHENTICATING

        ok, user_id, name = await self._mcp.authenticate_mobile(digits)
        if ok and user_id:
            ud.is_authenticated = True
            ud.user_id = user_id
            ud.state = SessionState.MAIN
            return GreetingAgent(), (f"Thanks {name or ''}. You're verified.".strip())

        ud.auth_attempts += 1
        if ud.auth_attempts >= 3:
            ud.state = SessionState.UNAUTHORIZED
            return UnauthorizedAgent(), (
                "Verification failed multiple times. Your access is locked."
            )
        return "That number could not be verified. Please try again, including your country code."