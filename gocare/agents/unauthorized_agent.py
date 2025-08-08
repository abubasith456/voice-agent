from __future__ import annotations

from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState


LOCKED_INSTRUCTIONS = "You are an unauthorized-state agent. The user failed verification. Kindly inform them that access is locked and provide safe next steps."


class UnauthorizedAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=LOCKED_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.UNAUTHORIZED
        await self.session.generate_reply(
            instructions=(
                "Your account access is locked due to failed verification attempts. "
                "Please try again later or use the official app to complete verification."
            )
        )
