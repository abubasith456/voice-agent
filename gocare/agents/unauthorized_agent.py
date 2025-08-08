from __future__ import annotations

from livekit.agents import Agent, RunContext, function_tool

from gocare.state import ConversationContext, SessionState


LOCKED_INSTRUCTIONS = (
    "You are GoCare Unauthorized Agent. The user failed verification. Kindly inform them that access is locked and provide safe next steps."
)


class UnauthorizedAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=LOCKED_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.userdata.state = SessionState.UNAUTHORIZED
        await self.session.generate_reply(
            instructions=(
                "Your account access is locked due to failed verification attempts. "
                "Please try again later or use the official app to complete verification."
            )
        )

    @function_tool
    async def restart_verification(self, context: RunContext) -> tuple[Agent[ConversationContext], str]:
        """Restart the verification process by returning to the greeting agent."""
        from gocare.agents.greeting_agent import GreetingAgent

        ud = self.session.userdata
        ud.user_mobile = None
        ud.auth_attempts = 0
        ud.is_authenticated = False
        ud.state = SessionState.GREETING
        return GreetingAgent(), "Okay. Please say your registered mobile number, including country code."