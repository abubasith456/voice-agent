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
    "If authentication succeeds, immediately call the function tool 'switch_to_greeting' with {user_id: <string>, name: <string>} to greet the user by name. "
    "Only when the user explicitly asks for personal information (profile, DOB, address, transactions, balances), switch to the MainAgent by calling 'switch_to_main' (no arguments). Then retrieve details using the external tool 'get_user_info' with {user_id: <string>} — the value must be the exact user_id returned by authentication. Never ask the user for their user ID. "
    "Authentication state: After a successful 'switch_to_greeting' call, the user is authenticated for the rest of the session. Never tell the user they are not authenticated. If a tool returns an error, silently retry with the stored user_id rather than asking for credentials. "
    "ID reuse: Persist the authenticated user_id in memory and always source user_id from memory for subsequent tool calls. Never infer it from the user's name or ask the user to repeat it. "
    "As you respond, include the user's name naturally in every message once known. "
    "Tool visibility: Never expose or print any tool-related syntax. Do NOT output code, JSON, or markers (e.g., <|python_start|>, <|python_end|>, tool(name=...), or any angle-bracket tags). Output plain natural language only. "
    "Silent tool rule: When invoking any external tool (including MCP tools), do not produce any user-facing text in that turn; respond only after the tool completes. "
    "Switching rule: When you invoke 'switch_to_greeting' or 'switch_to_main', do not produce any other user-facing text in that turn; the tool's returned message is the only output. "
    "If authentication fails, politely ask again; after multiple failures, inform that access is locked (but do not mention counts). "
    "Confidentiality: Never ask for or reveal secrets (password, PIN, OTP, CVV); refuse such requests. "
    "Do not mention tools, function names, schemas, or internal processes to the user. "
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
        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            "When calling external tools such as get_user_info, always pass user_id exactly as shown here. Do not ask the user for their user ID."
        )
        greet_text = (
            f"Hello {ud.user_name}. How can I help you today?" if ud.user_name else "Hello. How can I help you today?"
        )
        return GreetingAgent(extra_instructions=extra), greet_text

    @function_tool
    async def switch_to_main(self, context: RunContext) -> tuple[Agent, str]:
        """Switch to MainAgent for personal info queries using stored context (no arguments)."""
        ud = self.session.userdata
        extra = (
            f"Context: authenticated user_id='{ud.user_id}'. user_name='{ud.user_name}'. "
            "When calling external tools such as get_user_info, always pass user_id exactly as shown here. Never ask the user for their user ID."
        )
        return MainAgent(extra_instructions=extra), ""