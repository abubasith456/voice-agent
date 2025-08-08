from __future__ import annotations

from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

BASE_GREETING_INSTRUCTIONS = (
    "You are a post-auth greeting agent. The user has just been verified. "
    "Greet the user by their name (e.g., 'Hey John, welcome!') and let them know you can help with transactions. "
    "Keep replies concise and do not mention tools or internal processes."
)


class GreetingAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_GREETING_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        name = (self.session.userdata.user_name or "").strip()
        if name:
            msg = f"Hey {name}, welcome! How can I help you?"
        else:
            msg = "You're all set. How can I help with your transactions?"
        await self.session.generate_reply(instructions=msg)
