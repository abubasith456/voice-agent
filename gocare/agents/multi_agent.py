from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent
from gocare.agents.main_agent import MainAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are the session orchestrator. "
    "Flow: (1) Greet and request the registered mobile number (no need to mention country code). (2) When a valid mobile number appears, immediately call the external tool 'authenticate_user' with {mobile_number: <string>}. "
    "Immediately after a successful authentication result, call the function tool 'switch_to_greeting' in the same turn (do not wait for the user). "
    "Only when the user explicitly asks for personal information (profile, DOB, address, transactions, balances), switch to the MainAgent by calling 'switch_to_main' (no arguments). Then retrieve details using the external tool 'get_user_info' with {user_id: <string>} — the value must be the exact user_id returned by authentication. Never ask the user for their user ID. "
    "Domain scope: You ONLY help with banking/account tasks: authentication, profile info, balances, statements, transactions, and account updates. If the user asks for anything outside this scope (stories, jokes, general knowledge, unrelated tasks), politely refuse and state you can help with account and transactions only, then offer a relevant next step. Do not answer off-topic questions. "
    "As you respond, include the user's name naturally in context. Output exactly one sentence per turn unless listing short factual items (e.g., transactions). Do not repeat greetings. "
    "If authentication fails, politely ask again; after multiple failures, inform that access is locked (but do not mention counts). "
    "Confidentiality: Never ask for or reveal secrets (password, PIN, OTP, CVV); refuse such requests. "
    "Tooling Disclosure: Do not mention tool names, function calls, schemas, or internal processes to the user. "
    "Voice: Keep replies concise and natural. Read phone numbers as digit sequences, not as currency or amounts. Do not output protocol artifacts such as |end|."
)


class MultiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=BASE_MULTI_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.GREETING
        await self.session.generate_reply(
            instructions=(
                "Your next message must be exactly: 'Welcome. Please say your registered mobile number.' Do not add or prepend any other words."
            )
        )

    @function_tool
    async def switch_to_greeting(self, context: RunContext, user_id: str, name: str) -> tuple[Agent, str]:
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
            "When handling requests, if the user goes off-topic (e.g., stories, jokes, general knowledge), politely refuse and say you can help with account and transactions only."
        )
        single_line = (
            f"Hello {ud.user_name}, how can I assist you today?" if ud.user_name else "Hello, how can I assist you today?"
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