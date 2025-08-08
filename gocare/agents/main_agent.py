from __future__ import annotations

from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

BASE_MAIN_INSTRUCTIONS = (
    "System: You are the main assistant. The user is verified. Provide help with account and transactions. "
    "Style: Natural, conversational, and concise. Use contractions. Avoid robotic repetition. "
    "Name usage: Use the user's name sparingly (every few turns or when emphasis helps). Do not start every message with their name or re-greet. "
    "Follow-ups: If you add a follow-up, make it context-specific and short; don't ask the same question every time. "
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
        # Keep the first main prompt friendly but not repetitive
        prompt = (
            f"Welcome back, {name}. What do you need today?" if name else "What do you need today?"
        )
        await self.session.generate_reply(instructions=prompt)