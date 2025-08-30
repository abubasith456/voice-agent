from __future__ import annotations

from loguru import logger
from livekit.agents import Agent, RunContext, function_tool, JobContext

from app.state import SessionState

HELPLINE_INSTRUCTIONS = (
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


class HelplineAgent(Agent):
    def __init__(self, job_context: JobContext, extra_instructions: str = "") -> None:
        self.job_context = job_context
        logger.info("DEBUG - HelplineAgent.__init__ called")
        logger.info(f"DEBUG - extra_instructions: '{extra_instructions}'")

        instructions = HELPLINE_INSTRUCTIONS + "\n" + extra_instructions
        logger.info(f"DEBUG - Final instructions length: {len(instructions)}")

        super().__init__(instructions=instructions)
        logger.info("DEBUG - HelplineAgent.__init__ completed")

    async def on_enter(self) -> None:
        logger.info("DEBUG - HelplineAgent.on_enter() called")

        try:
            # Set session state
            logger.info("DEBUG - Setting session state to HELPLINE")
            self.session.userdata.state = SessionState.HELPLINE
            logger.info(f"DEBUG - Session state set to: {self.session.userdata.state}")

            # Check session data
            logger.info(
                f"DEBUG - Session userdata.user_name: '{getattr(self.session.userdata, 'user_name', 'NOT_SET')}'"
            )
            logger.info(
                f"DEBUG - Session userdata.user_id: '{getattr(self.session.userdata, 'user_id', 'NOT_SET')}'"
            )

            # Prepare welcome message
            welcome = "Hi there! I'm one of our customer support specialists. What can I help you with today?"
            logger.info(f"DEBUG - Welcome message prepared: '{welcome}'")

            # Generate the reply
            logger.info("DEBUG - About to call generate_reply()")
            result = await self.session.generate_reply(instructions=welcome)
            logger.info(f"DEBUG - generate_reply() completed with result: {result}")

            logger.info("DEBUG - HelplineAgent.on_enter() completed successfully")

        except Exception as e:
            logger.error(f"ERROR - Exception in HelplineAgent.on_enter(): {e}")
            logger.exception("Full exception traceback:")

            # Fallback attempt
            try:
                logger.info("DEBUG - Attempting fallback welcome message")
                await self.session.generate_reply(
                    instructions="Hello! How can I help you?"
                )
                logger.info("DEBUG - Fallback message sent successfully")
            except Exception as fallback_error:
                logger.error(f"ERROR - Even fallback failed: {fallback_error}")

    @function_tool
    async def end_session(self, context: RunContext) -> tuple[Agent, str]:
        """End the customer session"""
        logger.info("DEBUG - end_session() called")
        from app.agents.multi_agent import MultiAgent

        try:
            # Reset userdata properly
            if hasattr(self.session.userdata, "user_name"):
                self.session.userdata.user_name = None
            if hasattr(self.session.userdata, "user_id"):
                self.session.userdata.user_id = None
            if hasattr(self.session.userdata, "is_authenticated"):
                self.session.userdata.is_authenticated = False

            self.session.userdata.state = SessionState.UNAUTHORIZED
            logger.info("DEBUG - Session data cleared")

            farewell = "Thanks for banking with us! Have a wonderful day. Goodbye!"
            logger.info(f"DEBUG - Farewell message: '{farewell}'")

            await self.session.generate_reply(instructions=farewell)
            logger.info("DEBUG - Farewell message sent successfully")

            return (
                MultiAgent(
                    job_context=self.job_context,
                    user_name=self.session.userdata.user_name,
                    user_id=self.session.userdata.user_id,
                ),
                "Session ended successfully",
            )

        except Exception as e:
            logger.error(f"ERROR - Exception in end_session(): {e}")
            return (
                MultiAgent(
                    job_context=self.job_context,
                    user_name=self.session.userdata.user_name,
                    user_id=self.session.userdata.user_id,
                ),
                "Sorry, I encountered an error while trying to end the session. Please try again later.",
            )
