from __future__ import annotations

import re
from loguru import logger
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.main_agent import MainAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are the session orchestrator. "
    "Flow: (1) Greet and request the 4-digit OTP for authentication. (2) If the user enters a 4-digit OTP at the beginning, proceed to authenticate as normal. (3) If the user enters a 4-digit OTP at any intermediate state, confirm with the user by asking 'Is this the OTP you want to verify?' and only proceed with authentication if the user confirms. (4) When a 4-digit OTP appears and is confirmed by the user, immediately call the external tool 'authenticate_user' with {otp: <string>} or else confirm whether the user is authenticated or not. "
    "Immediately after a successful authentication result, call the function tool 'switch_to_greeting' in the same turn (do not wait for the user). Do not narrate that you are switching. "
    "Only when the user explicitly asks for personal information about the user, switch to the MainAgent by calling 'switch_to_main' (no arguments). Then retrieve details using the external tool 'get_user_info' with {user_id: <string>} — the value must be the exact user_id returned by authentication. Never ask the user for their user ID. "
    "Names: Do not use or guess a user name until it is returned by authentication. If no name is known yet, avoid addressing the user by name. Never invent names. "
    "Privacy: Do not state mapping like 'The user with number X is Y'. Just continue naturally using the name after authentication. "
    "Authentication state: After greeting handoff, the user is authenticated for the session. If asked, reply briefly ('You're verified.') without extra details. Never say 'not authenticated', 'logged in as', or 'a different user'. On tool error, ask for the OTP again without those phrases. "
    "Domain scope: You ONLY help with banking/account tasks: authentication, profile info, balances, statements, transactions, and account updates. If off-topic, politely refuse and offer a relevant next step. "
    "Style: Natural, conversational, and concise. Use contractions. Output exactly one sentence per turn unless listing short factual items; do not repeat greetings. "
    "Tooling Disclosure: Do not mention tool names, function calls, schemas, or internal processes to the user. Do not output code/markers. "
    "Forbidden characters/markers: never output [, ], <, >, {, }, backticks, or text that looks like a function call (e.g., name(args)). If your draft contains any of these, rewrite it as plain natural language. "
    "Voice: Read OTP digits individually; avoid protocol artifacts like |end|."
)


class MultiAgent(Agent):
    def __init__(self, user_name: str | None, user_id: str | None) -> None:
        self.user_name = user_name  # need to user this for the welcom the User please
        self.user_id = user_id
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING

        # Check if user name is already available from Flutter metadata
        user_name = (self.session.userdata.user_name or "").strip()

        if user_name:
            # User name is already available, provide a personalized greeting
            greeting_message = f"Welcome {user_name}! Please say the 4-digit OTP sent to your registered mobile."
            logger.info(f"Using personalized greeting for user: {user_name}")
        else:
            # No user name available, use generic greeting
            greeting_message = (
                "Welcome. Please say the 4-digit OTP sent to your registered mobile."
            )
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

        # Use the provided name or keep existing name from Flutter metadata
        final_name = (name or "").strip()
        if not final_name and ud.user_name:
            final_name = ud.user_name
            logger.info(f"Using existing user name from Flutter metadata: {final_name}")

        ud.user_id = user_id
        ud.user_name = final_name
        ud.is_authenticated = True
        ud.state = SessionState.MAIN

        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            "Stay strictly on account/transactions topics. If off-topic, politely refuse and offer a relevant next step."
        )

        # Create personalized greeting
        if ud.user_name:
            single_line = f"Hello {ud.user_name}, how can I assist you today?"
            logger.info(f"Created personalized greeting for: {ud.user_name}")
        else:
            single_line = "Hello, how can I assist you today?"
            logger.info("Created generic greeting (no user name)")

        return GreetingAgent(extra_instructions=extra), single_line

    @function_tool
    async def switch_to_main(self, context: RunContext) -> tuple[Agent, str]:
        """Switch to MainAgent for personal info queries using stored context (no arguments)."""
        ud = self.session.userdata
        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            "Stay strictly on account/transactions topics. If off-topic, politely refuse and offer a relevant next step."
        )
        return MainAgent(extra_instructions=extra), ""
