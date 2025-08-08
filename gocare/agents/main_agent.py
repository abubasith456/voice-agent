from __future__ import annotations

from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

BASE_MAIN_INSTRUCTIONS = (
    "System: You are the main assistant. The user is verified. Provide help with account and transactions. "
    "Include the user's name in every response naturally once known (e.g., 'Welcome John, ...', 'John, how can I help?'). "
    "Use available external capabilities implicitly without mentioning tools or internal processes. "
    "Do not reveal or request secrets (password, PIN, OTP, CVV). Keep replies concise and voice-friendly."
)


class MainAgent(Agent):
    def __init__(self, extra_instructions: str | None = None) -> None:
        instructions_text = BASE_MAIN_INSTRUCTIONS
        if extra_instructions:
            instructions_text = instructions_text + " " + extra_instructions
        super().__init__(instructions=instructions_text)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.MAIN
        name = (self.session.userdata.user_name or "").strip()
        prompt = f"Welcome {name}, how can I help with your transactions today?" if name else "How can I help with your transactions today?"
        await self.session.generate_reply(instructions=prompt)