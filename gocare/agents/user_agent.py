from __future__ import annotations

from typing import Any
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import (
    contains_sensitive_request,
    refusal_message,
    log_sensitive_attempt,
)
from gocare.mcp import MCPClient

BASE_USER_INSTRUCTIONS = (
    "System: You are a post-auth assistant. The user is verified. Answer account/transaction questions. "
    "When asked about profile or transactions, retrieve the necessary information without mentioning tools or internal processes. "
    "Security: Never reveal or request passwords, PINs, OTPs, or CVV; refuse and log attempts. "
    "Voice: Keep answers short and natural; summarize transactions unless asked to enumerate. Read numbers as digit sequences, not currency, unless explicitly about money."
)


class UserAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_USER_INSTRUCTIONS)
        self._mcp = MCPClient()

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions="How can I help with your transactions today?"
        )

    @function_tool
    async def get_user_info(self, context: RunContext) -> dict[str, Any] | str:
        """Get the user's profile and recent transactions via MCP."""
        ud = self.session.userdata
        if not ud.is_authenticated or not ud.user_id:
            return "We need to complete verification first."
        return await self._mcp.get_user_info(ud.user_id)

    @function_tool
    async def refuse_sensitive(self, context: RunContext, user_text: str) -> str:
        ud = self.session.userdata
        log_sensitive_attempt(ud.user_id, user_text)
        return refusal_message()
