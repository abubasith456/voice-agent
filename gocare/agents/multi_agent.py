from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.main_agent import MainAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are the session orchestrator. "
    "Flow: (1) After connection, welcome the user using the known display name if available (from session context), then ask for the registered mobile number (no need to mention country code). "
    "When a valid mobile number appears at ANY time in the conversation, immediately call the external tool 'authenticate_user' with {mobile_number: <string>} or else confirm the user is authentication mobile number or not. "
    "Immediately after a successful authentication result, call the function tool 'switch_to_greeting' in the same turn (do not wait for the user). Do not narrate that you are switching. "
    "Only when the user explicitly asks for personal information about the user, switch to the MainAgent by calling 'switch_to_main' (no arguments). Then retrieve details using the external tool 'get_user_info' with {user_id: <string>} — the value must be the exact user_id returned by authentication. Never ask the user for their user ID. "
    "Names: You may use a provided display name from the room/session context for the initial welcome only; after authentication, use the verified name. Never invent names. "
    "Privacy: Do not state mapping like 'The user with number X is Y'. Just continue naturally using the name after authentication. "
    "Authentication state: After greeting handoff, the user is authenticated for the session. If asked, reply briefly ('You're verified.') without extra details. Never say 'not authenticated', 'logged in as', or 'a different user'. On tool error, ask for the mobile again without those phrases. "
    "Domain scope: You ONLY help with banking/account tasks: authentication, profile info, balances, statements, transactions, and account updates. If off-topic, politely refuse and offer a relevant next step. "
    "Style: Natural, conversational, and concise. Use contractions. Output exactly one sentence per turn unless listing short factual items; do not repeat greetings. "
    "Tooling Disclosure: Do not mention tool names, function calls, schemas, or internal processes to the user. Do not output code/markers. "
    "Forbidden characters/markers: never output [, ], <, >, {, }, backticks, or text that looks like a function call (e.g., name(args)). If your draft contains any of these, rewrite it as plain natural language. "
    "Voice: Read phone numbers as digit sequences, not currency; avoid protocol artifacts like |end|."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING
        name = (self.session.userdata.user_name or "").strip()
        if name:
            prompt = (
                f"Your next message must be exactly: 'Welcome {name}. Please say your registered mobile number.' Do not add or prepend any other words."
            )
        else:
            prompt = (
                "Your next message must be exactly: 'Welcome. Please say your registered mobile number.' Do not add or prepend any other words."
            )
        await self.session.generate_reply(instructions=prompt)

    @function_tool
    async def switch_to_greeting(
        self, context: RunContext, user_id: str, name: str
    ) -> tuple[Agent, str]:
        """Switch to GreetingAgent after successful authentication."""
        ud = self.session.userdata
        # Guard against unintended re-greeting when already authenticated
        if ud.is_authenticated and ud.user_id:
            return self, ""
        ud.user_id = user_id
        ud.user_name = (name or "").strip()
        ud.is_authenticated = True
        ud.state = SessionState.MAIN
        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            "Stay strictly on account/transactions topics. If off-topic, politely refuse and offer a relevant next step."
        )
        single_line = (
            f"Hello {ud.user_name}, how can I assist you today?"
            if ud.user_name
            else "Hello, how can I assist you today?"
        )
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
