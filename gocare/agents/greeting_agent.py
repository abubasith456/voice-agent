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
    def __init__(self, extra_instructions: str | None = None) -> None:
        instructions_text = BASE_GREETING_INSTRUCTIONS
        if extra_instructions:
            instructions_text = instructions_text + " " + extra_instructions
        super().__init__(instructions=instructions_text)

    async def on_enter(self) -> None:
        # Stay in MAIN and let the handoff message from switch_to_greeting be the only output
        self.session.userdata.state = SessionState.MAIN
        return
