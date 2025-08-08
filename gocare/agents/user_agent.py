from __future__ import annotations

from typing import Any, AsyncIterable
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import contains_sensitive_request, refusal_message, log_sensitive_attempt
from gocare.mcp import MCPClient

BASE_USER_INSTRUCTIONS = (
    "System: You are GoCare User Agent. The user is verified. Answer account/transaction questions. "
    "Tools: Use query_user (calls MCP get_user_info) when user asks about balances, recent activity, or details. "
    "Security: Never reveal or request passwords, PINs, OTPs, or CVV; refuse and log attempts. "
    "Voice: Keep answers short, natural, and avoid reading long lists unless asked; summarize recent transactions."
)


class UserAgent(Agent):
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
    async def query_user(self, context: RunContext, question: str) -> str:
        """Fetch user info via MCP and return a concise, voice-friendly answer."""
        ud = self.session.userdata
        if contains_sensitive_request(question):
            log_sensitive_attempt(ud.user_id, question)
            return refusal_message()
        if not ud.is_authenticated or not ud.user_id:
            return "We need to complete verification first."

        info = await self._mcp.get_user_info(ud.user_id)
        name = info.get("name") or ""
        dob = info.get("dob") or ""
        tx = info.get("transactions")
        # transactions may be a serialized string; keep response very short
        if any(k in question.lower() for k in ["transaction", "activity", "spend", "spent", "recent"]):
            return f"{name}, I retrieved your recent activity. What would you like to know about it?"
        if any(k in question.lower() for k in ["dob", "date of birth", "name", "profile"]):
            return f"Your profile shows name {name}."
        return "I retrieved your account details. What would you like to know specifically?"