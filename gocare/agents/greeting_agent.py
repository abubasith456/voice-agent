from __future__ import annotations

import re
from dataclasses import asdict
from typing import Optional

from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.security import refusal_message, log_sensitive_attempt
from gocare.agents.main_agent import MainAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")


GREETING_INSTRUCTIONS = (
    "You are GoCare Greeting Agent. Your job is to greet the user and collect their registered mobile number. "
    "Do not ask for passwords, OTPs, or PINs. If the user asks for such info, refuse politely. "
    "Once the user provides a valid mobile number, call the function submit_mobile with the parsed number in E.164-like format. "
    "Keep replies concise and speech-friendly."
)


class GreetingAgent(Agent[ConversationContext]):
    def __init__(self) -> None:
        super().__init__(instructions=GREETING_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Welcome to GoCare. To continue, please say your registered mobile number, including country code."
            )
        )

    @function_tool
    async def submit_mobile(self, context: RunContext, mobile: str) -> str | tuple[Agent[ConversationContext], str]:
        """Verify the user's mobile number and transition to the main agent when successful.
        Args:
            mobile: The user's registered mobile number spoken by the user.
        Returns:
            If verification succeeds, returns a tuple of (MainAgent, success message) to hand off. Otherwise, returns an error message.
        """
        ud = self.session.userdata
        digits = re.sub(r"[^\d+]", "", mobile)
        if not digits:
            return "I couldn't detect a number. Please say your full mobile number, including country code."

        ud.user_mobile = digits
        ud.state = SessionState.AUTHENTICATING

        # Simple demo verification: accept numbers with 10+ digits
        verified = len([c for c in digits if c.isdigit()]) >= 10
        if verified:
            ud.is_authenticated = True
            ud.user_id = f"user:{digits[-4:]}"
            ud.state = SessionState.MAIN
            main = MainAgent()
            return main, "Thanks. You're verified. How can I help with your transactions today?"

        ud.auth_attempts += 1
        if ud.auth_attempts >= 3:
            ud.state = SessionState.UNAUTHORIZED
            return "Verification failed multiple times. Please try again later."
        return "That number could not be verified. Please try again, including your country code."

    @function_tool
    async def change_number(self, context: RunContext) -> str:
        """Reset the current number and start over the verification process."""
        ud = self.session.userdata
        ud.user_mobile = None
        ud.is_authenticated = False
        ud.auth_attempts = 0
        ud.state = SessionState.GREETING
        return "Okay. Please say your registered mobile number, including country code."