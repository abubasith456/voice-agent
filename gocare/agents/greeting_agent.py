from __future__ import annotations

from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

BASE_GREETING_INSTRUCTIONS = (
    "You are a post-auth greeting agent. The user has just been verified. "
    "Offer a friendly, concise welcome and let them know you can help with transactions."
)


class GreetingAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_GREETING_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        await self.session.generate_reply(
            instructions=(
                "You're all set. How can I help with your transactions?"
            )
        )
