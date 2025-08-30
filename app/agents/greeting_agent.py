from __future__ import annotations

from livekit.agents import Agent

from app.state import ConversationContext, SessionState

BASE_GREETING_INSTRUCTIONS = (
    "You are a post-auth assistant. The user has been verified. "
    "Style: Natural, conversational, and concise. Use contractions. Avoid robotic repetition. "
    "Name usage: Use the user's name sparingly (roughly every few turns or when emphasis/clarity helps). Do not start every message with their name or with 'Hello'. "
    "Greetings: Do not re-greet after the initial welcome. "
    "Follow-ups: Do not append the same generic question (e.g., 'How can I help you today?') to every reply. If you offer a follow-up, make it context-specific and short (max ~5 words), and not every time. "
    "Content: Answer the user's request directly and succinctly. If they ask for personal info, retrieve it via available tools without exposing tool usage. Do not list options or menus unless explicitly requested. "
    "Do not mention tools, function calls, schemas, or internal processes."
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
