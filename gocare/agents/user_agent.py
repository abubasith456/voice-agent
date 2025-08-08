from __future__ import annotations

from typing import Any
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import contains_sensitive_request, refusal_message, log_sensitive_attempt

BASE_USER_INSTRUCTIONS = (
    "System: You are GoCare User Agent. The user is verified. Answer account/transaction questions. "
    "When asked about profile or transactions, call MCP tool 'get_user_info' with {user_id: <string>}. "
    "Security: Never reveal or request passwords, PINs, OTPs, or CVV; refuse and log attempts. "
    "Voice: Keep answers short and natural; summarize transactions unless asked to enumerate."
)


class UserAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_USER_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.instructions = BASE_USER_INSTRUCTIONS
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions="How can I help with your transactions today?"
        )

    @function_tool
    async def refuse_sensitive(self, context: RunContext, user_text: str) -> str:
        ud = self.session.userdata
        log_sensitive_attempt(ud.user_id, user_text)
        return refusal_message()