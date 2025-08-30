from __future__ import annotations

from loguru import logger
from livekit.agents import RunContext, function_tool

from app.agents.base_agent import BaseAgent
from app.state import SessionState


class HelplineAgent(BaseAgent):
    def get_base_instructions(self) -> str:
        return (
            "You're a human customer support specialist at the bank.\n\n"
            "Your role:\n"
            "- Help customers with any banking questions or issues\n"
            "- Be friendly, professional, and understanding\n"
            "- Solve problems step by step\n"
            "- Listen carefully and provide clear solutions\n\n"
            "CONVERSATION STYLE:\n"
            "- Talk exactly like a real human would\n"
            "- Use natural speech patterns and pauses\n"
            "- Show empathy and understanding\n"
            "- Be patient and helpful\n"
            "- Never sound robotic or scripted\n\n"
            "FORMATTING RULES:\n"
            "- No special characters, symbols, or markdown\n"
            "- No bullet points or lists in responses\n"
            "- Write in natural, flowing conversation\n"
            "- Sound like you're speaking, not writing\n\n"
            "Session management:\n"
            "- If customer says goodbye, end call, or wants to logout: use end_session\n"
            "- Listen for phrases like 'that's all', 'thanks bye', 'end session'\n"
        )

    async def on_enter(self) -> None:
        """Initialize the helpline agent."""
        await super().on_enter()
        self.session.userdata.state = SessionState.HELPLINE
        
        welcome = "Hi there! I'm one of our customer support specialists. What can I help you with today?"
        await self.session.generate_reply(instructions=welcome)
        logger.info(f"HelplineAgent started for user: {self.user_name}")

    @function_tool
    async def end_session(self, context: RunContext) -> tuple:
        """End the customer session"""
        from app.agents.auth_agent import AuthAgent
        
        # Reset userdata
        self.session.userdata.user_name = None
        self.session.userdata.user_id = None
        self.session.userdata.is_authenticated = False
        self.session.userdata.state = SessionState.UNAUTHORIZED
        
        farewell = "Thanks for banking with us! Have a wonderful day. Goodbye!"
        await self.session.generate_reply(instructions=farewell)
        
        return (
            AuthAgent(
                job_context=self.job_context,
                user_name=None,
                user_id=None
            ),
            "Session ended successfully",
        )
