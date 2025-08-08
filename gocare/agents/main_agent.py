from __future__ import annotations

from dataclasses import asdict
from typing import Any
from loguru import logger

from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import contains_sensitive_request, refusal_message, log_sensitive_attempt

MAIN_INSTRUCTIONS = (
    "You are GoCare Main Agent. The user is verified. Help them with transaction-related questions. "
    "Never provide or ask for passwords, PINs, or OTPs. If the user requests these, refuse politely. "
    "Use the list_transactions tool if the user asks about recent activity. Keep replies concise and voice-friendly."
)


class MainAgent(Agent[ConversationContext]):
    def __init__(self) -> None:
        super().__init__(instructions=MAIN_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions="You're verified. How can I help with your transactions today?"
        )

    @function_tool
    async def list_transactions(self, context: RunContext, last_n: int = 3) -> list[dict[str, Any]]:
        """Return a list of the user's most recent transactions for demo purposes.
        Args:
            last_n: The number of recent transactions to return (max 10).
        Returns:
            A list of transaction dicts with fields: date, merchant, amount, currency, type.
        """
        ud = self.session.userdata
        if not ud.is_authenticated:
            return []
        n = max(1, min(10, int(last_n)))
        demo = [
            {"date": "2025-07-01", "merchant": "Grocery Mart", "amount": -42.35, "currency": "USD", "type": "debit"},
            {"date": "2025-06-29", "merchant": "Salary", "amount": 3200.00, "currency": "USD", "type": "credit"},
            {"date": "2025-06-28", "merchant": "Coffee House", "amount": -4.75, "currency": "USD", "type": "debit"},
            {"date": "2025-06-27", "merchant": "Utility Power", "amount": -120.00, "currency": "USD", "type": "debit"},
        ]
        return demo[:n]

    @function_tool
    async def refuse_sensitive(self, context: RunContext, user_text: str) -> str:
        """Refuse requests for passwords, OTPs, PINs, or similar secrets and log the attempt."""
        ud = self.session.userdata
        log_sensitive_attempt(ud.user_id, user_text)
        return refusal_message()