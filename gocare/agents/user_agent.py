from __future__ import annotations

from typing import Any, AsyncIterable
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import contains_sensitive_request, refusal_message, log_sensitive_attempt
from gocare.mcp import MCPClient

BASE_USER_INSTRUCTIONS = (
    "You are GoCare User Agent. The user is verified. Help with their account and transactions. "
    "Never provide or ask for passwords, PINs, or OTPs. If asked, refuse and log. "
    "Use query_user tool for user questions. Keep responses concise and voice-friendly."
)


class UserAgent(Agent[ConversationContext]):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_USER_INSTRUCTIONS)
        self._mcp = MCPClient()

    async def on_enter(self) -> None:
        self.instructions = BASE_USER_INSTRUCTIONS
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions="How can I help with your transactions today?"
        )

    @function_tool
    async def query_user(self, context: RunContext, question: str) -> AsyncIterable[str] | str:
        """Stream an answer to the user's question via MCP."""
        ud = self.session.userdata
        if contains_sensitive_request(question):
            log_sensitive_attempt(ud.user_id, question)
            return refusal_message()
        if not ud.is_authenticated or not ud.user_id:
            return "We need to complete verification first."
        return self._mcp.stream_query(ud.user_id, question)