from __future__ import annotations

import re
from loguru import logger
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.main_agent import MainAgent

USER_ID_REGEX = re.compile(r"^u\d{3}$")  # Matches u001, u002, etc.
OTP_REGEX = re.compile(r"^\d{4}$")  # Matches 4-digit OTP from CSV

BASE_MULTI_INSTRUCTIONS = (
    "System: You are the session orchestrator for a banking voice assistant. "
    "Authentication Flow: (1) Welcome the user by name. (2) Ask for the 4-digit OTP directly. (3) When user provides the 4-digit OTP, call 'authenticate_user' with {user_id: <string>, otp: <string>} to verify. (4) After successful authentication, immediately call 'switch_to_greeting' with the returned user_id and name. "
    "User ID: Use the user_id that is already available in the session context. "
    "OTP Format: Must be exactly 4 digits (e.g., 1234). "
    "Error Handling: If OTP is invalid, ask for OTP again. "
    "Only when the user explicitly asks for personal information, switch to MainAgent by calling 'switch_to_main' (no arguments). Then retrieve details using 'get_user_info' with {user_id: <string>} — the value must be the exact user_id returned by authentication. "
    "Names: Use the user name available in the session context for personalized greetings. "
    "Privacy: Do not state mapping like 'The user with ID X is Y'. Just continue naturally using the name after authentication. "
    "Authentication state: After greeting handoff, the user is authenticated for the session. If asked, reply briefly ('You're verified.') without extra details. Never say 'not authenticated', 'logged in as', or 'a different user'. "
    "Domain scope: You ONLY help with banking/account tasks: authentication, profile info, balances, statements, transactions, and account updates. If off-topic, politely refuse and offer a relevant next step. "
    "Style: Natural, conversational, and concise. Use contractions. Output exactly one sentence per turn unless listing short factual items; do not repeat greetings. "
    "Tooling Disclosure: Do not mention tool names, function calls, schemas, or internal processes to the user. Do not output code/markers. "
    "Forbidden characters/markers: never output [, ], <, >, {, }, backticks, or text that looks like a function call (e.g., name(args)). If your draft contains any of these, rewrite it as plain natural language. "
    "Voice: When asking for OTP, say 'Please provide your four-digit OTP' or 'Please enter your four-digit OTP'. Do not say '4-digit OTP' as it sounds robotic. Read OTPs as individual digits when confirming."
)


class MultiAgent(Agent):
    def __init__(
        self, user_name: str | None = None, user_id: str | None = None
    ) -> None:
        self.user_name = user_name  # need to user this for the welcom the User please
        self.user_id = user_id
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING

        # Set user data in conversation context immediately
        if self.user_name:
            self.session.userdata.user_name = self.user_name
        if self.user_id:
            self.session.userdata.user_id = self.user_id

        print(
            f"MultiAgent on_enter: user_name='{self.user_name}', user_id='{self.user_id}'"
        )

        if self.user_name and self.user_id:
            # User name and ID are available
            greeting_message = f"Welcome {self.user_name}! Please provide your four-digit OTP to continue."
            logger.info(
                f"Using personalized greeting for user: {self.user_name} with ID: {self.user_id}"
            )
        else:
            # No user name available, use generic greeting
            greeting_message = "Welcome! Please provide your four-digit OTP to continue."
            logger.info("Using generic greeting (no user name available)")

        await self.session.generate_reply(
            instructions=(
                f"Your next message must be exactly: '{greeting_message}' Do not add or prepend any other words."
            )
        )

    @function_tool
    async def switch_to_greeting(
        self, context: RunContext, user_id: str, name: str
    ) -> tuple[Agent, str]:
        """Switch to GreetingAgent after successful authentication."""
        ud = self.session.userdata
        # Guard against unintended re-greeting when already authenticated
        if ud.is_authenticated and ud.user_id:
            return self, ""

        # Use the provided name or keep existing name from session context
        final_name = (name or "").strip()
        if not final_name and ud.user_name:
            final_name = ud.user_name
            logger.info(f"Using existing user name from session context: {final_name}")

        ud.user_id = user_id
        ud.user_name = final_name
        ud.is_authenticated = True
        ud.state = SessionState.MAIN

        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            f"When calling MCP tools like 'get_user_info', 'get_user_bill', 'get_user_contact', or 'get_user_last_login', always use user_id='{ud.user_id}'. "
            "Stay strictly on account/transactions topics. If off-topic, politely refuse and offer a relevant next step. "
            "IMPORTANT: Never mention tool names, function calls, or internal processes to the user. Keep responses natural and conversational."
        )

        # Create personalized greeting with data offer
        if ud.user_name:
            single_line = f"How can I help you {ud.user_name} with your data?"
            logger.info(f"Created personalized greeting for: {ud.user_name}")
        else:
            single_line = "How can I help you with your data?"
            logger.info("Created generic greeting (no user name)")

        return GreetingAgent(extra_instructions=extra), single_line

    @function_tool
    async def switch_to_main(self, context: RunContext) -> tuple[Agent, str]:
        """Switch to MainAgent for personal info queries using stored context (no arguments)."""
        ud = self.session.userdata
        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            f"When calling MCP tools like 'get_user_info', 'get_user_bill', 'get_user_contact', or 'get_user_last_login', always use user_id='{ud.user_id}'. "
            "Stay strictly on account/transactions topics. If off-topic, politely refuse and offer a relevant next step. "
            "IMPORTANT: Never mention tool names, function calls, or internal processes to the user. Keep responses natural and conversational."
        )
        return MainAgent(extra_instructions=extra), ""
