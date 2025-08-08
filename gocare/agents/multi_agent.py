from __future__ import annotations

import re
from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState
from gocare.agents.greeting_agent import GreetingAgent

MOBILE_REGEX = re.compile(r"(\+?\d[\d\- ]{7,14}\d)")

BASE_MULTI_INSTRUCTIONS = (
    "System: You are the session orchestrator. "
    "Flow: (1) Greet and request the registered mobile number (no need to mention country code). (2) When a valid mobile number appears, immediately call the external tool 'authenticate_user' with {mobile_number: <string>}. "
    "If authentication succeeds, immediately call the function tool 'switch_to_greeting' with {user_id: <string>, name: <string>} to greet the user by name. "
    "Only when the user explicitly asks for personal information (profile, DOB, address, transactions, balances), retrieve details using the external tool 'get_user_info' with {user_id: <string>} — the value must be the exact user_id returned by authentication, not the user's name. "
    "As you respond, include the user's name naturally in every message once known. "
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
        ud.user_id = user_id
        ud.user_name = (name or "").strip()
        ud.is_authenticated = True
        ud.state = SessionState.MAIN
        # Return greeting agent, but let it speak the welcome-by-name
        return GreetingAgent(), ""