from __future__ import annotations

import re
from dataclasses import asdict
from typing import Optional

from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import refusal_message, log_sensitive_attempt
from gocare.agents.user_agent import UserAgent
from gocare.agents.unauthorized_agent import UnauthorizedAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")


BASE_GREETING_INSTRUCTIONS = (
    "You are GoCare Greeting Agent. The user has just been verified. "
    "Offer a friendly, concise welcome, then transition to the UserAgent."
)


class GreetingAgent(Agent[ConversationContext]):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_GREETING_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.instructions = BASE_GREETING_INSTRUCTIONS
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions=(
                "Welcome to GoCare. You're all set. I'll connect you to your assistant to help with your transactions."
            )
        )
        # Immediately hand off to UserAgent
        await self.session.handoff(UserAgent(), "How can I help with your transactions today?")

    # The mobile collection is now handled by MultiAgent