from __future__ import annotations

from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

BASE_GREETING_INSTRUCTIONS = (
    "You are a post-auth greeting agent. The user has just been verified. "
    "Greet the user by their name (e.g., 'Hello John. How can I help you today?'). "
    "Do not list options, do not provide menus, and do not append any suggestions. Ask only a single concise question. "
    "Keep replies concise and do not mention tools or internal processes."
)


class GreetingAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_GREETING_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        name = (self.session.userdata.user_name or "").strip()
        if name:
            exact = f"Hello {name}. How can I help you today?"
        else:
            exact = "Hello. How can I help you today?"
        await self.session.generate_reply(
            instructions=(
                f"Your next message must be exactly: '{exact}' Do not add, prepend, or append any other words."
            )
        )
