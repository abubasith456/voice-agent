from __future__ import annotations

import asyncio
from typing import Optional
from loguru import logger

from gocare.state import ConversationContext, SessionState
from gocare.agents import GreetingAgent, MainAgent


class MultiAgentManager:
    def __init__(self) -> None:
        self.ctx = ConversationContext()
        self.greeting = GreetingAgent()
        self.main = MainAgent()

    async def start(self) -> str:
        # Enter greeting first
        return await self.greeting.on_enter(self.ctx) or "Hello"

    async def handle_user_text(self, text: str) -> str:
        logger.info("User said: {}", text)
        self.ctx.last_user_message = text

        # Allow number change during auth
        if "change number" in text.lower():
            self.ctx.reset_auth()
            return await self.greeting.on_enter(self.ctx) or "Please share your number."

        if self.ctx.state in (SessionState.GREETING, SessionState.AUTHENTICATING):
            # If we are in GREETING and we get a number, GreetingAgent moves to AUTHENTICATING.
            response = await self.greeting.on_user_message(text, self.ctx)
            if self.ctx.state == SessionState.AUTHENTICATING and self.ctx.user_mobile:
                # Simulate verification for demo
                verified = await self._verify_mobile(self.ctx.user_mobile)
                if verified:
                    self.ctx.is_authenticated = True
                    self.ctx.user_id = f"user:{self.ctx.user_mobile[-4:]}"
                    await self.greeting.on_exit(self.ctx)
                    enter_msg = await self.main.on_enter(self.ctx)
                    return enter_msg or "You're verified."
                else:
                    self.ctx.auth_attempts += 1
                    if self.ctx.auth_attempts >= 3:
                        self.ctx.state = SessionState.UNAUTHORIZED
                        return "Verification failed. Please try again later."
                    return "That number could not be verified. Please try again."
            return response or ""

        if self.ctx.state == SessionState.MAIN:
            return await self.main.on_user_message(text, self.ctx) or ""

        if self.ctx.state == SessionState.UNAUTHORIZED:
            return "Access is locked due to failed verification attempts."

        return "I'm not sure how to proceed."

    async def _verify_mobile(self, mobile: str) -> bool:
        # Placeholder verification: accept numbers with 10+ digits
        digits = [c for c in mobile if c.isdigit()]
        await asyncio.sleep(0.2)
        return len(digits) >= 10