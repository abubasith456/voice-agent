from __future__ import annotations

import re
from loguru import logger
from livekit.agents import Agent, RunContext, function_tool, JobContext

from gocare.state import ConversationContext, SessionState
from gocare.agents.main_agent import MainAgent

USER_ID_REGEX = re.compile(r"^u\d{3}$")
OTP_REGEX = re.compile(r"^\d{4}$")

AUTHENTICATION_INSTRUCTIONS = (
    "ROLE:\n"
    "You are a friendly bank representative verifying a customer's 4-digit security OTP code.\n"
    "Follow the exact steps provided. Do not improvise.\n\n"
    "WORKFLOW:\n"
    "1. Greet the user warmly ONCE and ask for their 4-digit OTP code.\n"
    "2. When 4 numbers are provided, immediately call the authenticate_user tool with the exact user_id from session.\n"
    "3. Wait for the authenticate_user result.\n"
    "4. If authentication SUCCESSFUL → IMMEDIATELY call switch_to_main. Make this switch without saying anything to the user.\n"
    "5. If authentication FAILS → Politely ask them to try again.\n"
    "6. After each tool call, always take the next action — never leave silence.\n\n"
    "POST-AUTHENTICATION RULES:\n"
    "- On SUCCESS: Do NOT speak to the user, do NOT say 'you are authenticated', do NOT congratulate.\n"
    "- On FAILURE: The authentication failed. Respond naturally and ask them to try again. Be conversational and helpful.\n"
    "- The MainAgent will handle the welcome message after switching — you must remain silent.\n"
    "- Absolutely NO confirmation phrases after success.\n\n"
    "SECURITY:\n"
    "- Only use the exact user_id from session — never modify it.\n"
    "- Never expose OTPs or any sensitive values back to the user.\n\n"
    "STYLE:\n"
    "- Sound natural, like a person on the phone.\n"
    "- Responses should be short and friendly.\n"
    "- No technical or internal process explanations.\n\n"
    "FORMATTING:\n"
    "- No asterisks, hashtags, brackets, markdown, or symbols.\n"
    "- Plain spoken text only.\n\n"
    "REMINDER:\n"
    "- After successful authentication: switch agents in complete silence.\n"
    "- Let MainAgent speak first after switching.\n"
)


class MultiAgent(Agent):
    def __init__(
        self,
        job_context: JobContext,
        user_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.job_context = job_context
        self.user_name = user_name
        self.user_id = user_id

        session_context = (
            f"\nCRITICAL SESSION INFO:\n"
            f"The user's name is: {self.user_name}\n"
            f"The user's ID is: {self.user_id}\n"
            f"IMPORTANT: When calling authenticate_user, you MUST use user_id='{self.user_id}' EXACTLY as written.\n"
            f"DO NOT change or modify this ID. DO NOT add letters. Use the exact number: {self.user_id}\n"
        )

        super().__init__(instructions=AUTHENTICATION_INSTRUCTIONS + session_context)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.AUTHENTICATING
        self.session.userdata.user_name = self.user_name
        self.session.userdata.user_id = self.user_id

        # Direct, natural greeting
        if self.user_name:
            greeting = f"Hey {self.user_name}! I'll need your four-digit security OTP code to get you into your account."
        else:
            greeting = "Hello! Please give me your four-digit security code so I can help you access your account."

        await self.session.generate_reply(instructions=f"Greeting: {greeting}")

    @function_tool
    async def switch_to_main(self, context: RunContext) -> tuple[Agent, str]:
        """Switch to MainAgent after successful authentication"""
        userdata = self.session.userdata
        userdata.is_authenticated = True

        # Simple context without exposing user ID to user
        main_context = (
            f"User {userdata.user_name} is authenticated. "
            f"Always use user_id '{userdata.user_id}' for all MCP calls. "
            "Be helpful and conversational. No special formatting."
        )

        logger.info(f"Successfully switching to MainAgent for {userdata.user_name}")

        # Return with empty message - let MainAgent handle the greeting
        return (
            MainAgent(job_context=self.job_context, extra_instructions=main_context),
            "",
        )
