from __future__ import annotations

from loguru import logger
from livekit.agents import Agent

from gocare.state import ConversationContext, SessionState

BASE_MAIN_INSTRUCTIONS = (
    "System: You are the main assistant. The user is verified. Provide help with account and transactions. "
    "Style: Natural, conversational, and concise. Use contractions. Avoid robotic repetition. "
    "Name usage: Use the user's name sparingly (every few turns or when emphasis helps). Do not start every message with their name or re-greet. "
    "Follow-ups: If you add a follow-up, make it context-specific and short; don't ask the same question every time. "
    "Use available external capabilities implicitly without mentioning tools or internal processes. "
    "Do not reveal or request secrets (password, PIN, OTP, CVV). Keep replies concise and voice-friendly. "
    "IMPORTANT: Never mention tool names, function calls, schemas, or internal processes to the user. Keep responses natural and conversational. "
    "Forbidden characters/markers: never output [, ], <, >, {, }, backticks, or text that looks like a function call (e.g., name(args)). If your draft contains any of these, rewrite it as plain natural language."
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
        
        if name:
            # Keep the first main prompt friendly but not repetitive
            prompt = f"Welcome back, {name}. What would you like to know about your data?"
            logger.info(f"MainAgent greeting user by name: {name}")
        else:
            prompt = "What would you like to know about your data?"
            logger.info("MainAgent using generic greeting (no user name)")
        
        await self.session.generate_reply(instructions=prompt)