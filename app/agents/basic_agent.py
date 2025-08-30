from __future__ import annotations

from loguru import logger
from livekit.agents import JobContext

from app.agents.base_agent import BaseAgent
from app.state import SessionState


class BasicAgent(BaseAgent):
    """Simple voice-to-voice assistance agent without authentication."""
    
    def get_base_instructions(self) -> str:
        return (
            "You are a helpful voice assistant providing basic customer service.\n\n"
            "CAPABILITIES:\n"
            "- Answer general questions about services\n"
            "- Provide basic information\n"
            "- Be conversational and helpful\n\n"
            "CONVERSATION STYLE:\n"
            "- Natural, friendly, and conversational\n"
            "- Keep responses concise and clear\n"
            "- Use the customer's name when available\n"
            "- Sound like a real person, not a robot\n\n"
            "FORMATTING:\n"
            "- No special characters, symbols, or markdown\n"
            "- Plain spoken text only\n"
            "- Natural flowing conversation\n\n"
            "LIMITATIONS:\n"
            "- Cannot access personal account information\n"
            "- Cannot perform authentication\n"
            "- Cannot access sensitive data\n"
            "- Direct customers to human support for complex issues\n"
        )
    
    async def on_enter(self) -> None:
        """Initialize the basic agent session."""
        await super().on_enter()
        self.session.userdata.state = SessionState.MAIN
        
        # Simple greeting
        if self.user_name:
            greeting = f"Hello {self.user_name}! How can I help you today?"
        else:
            greeting = "Hello! How can I help you today?"
        
        await self.session.generate_reply(instructions=greeting)
        logger.info(f"BasicAgent started for user: {self.user_name}")