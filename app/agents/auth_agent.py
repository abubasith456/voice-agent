from __future__ import annotations

import re
from loguru import logger
from livekit.agents import RunContext, function_tool

from app.agents.base_agent import BaseAgent
from app.state import SessionState

OTP_REGEX = re.compile(r"^\d{4}$")


class AuthAgent(BaseAgent):
    """Handles user authentication with OTP verification."""
    
    def get_base_instructions(self) -> str:
        return (
            "ROLE:\n"
            "You are a friendly bank representative verifying a customer's 4-digit security OTP code.\n"
            "Follow the exact steps provided. Do not improvise.\n\n"
            "WORKFLOW:\n"
            "1. Greet the user warmly ONCE and ask for their 4-digit OTP code.\n"
            "2. When 4 numbers are provided, immediately call the authenticate_user tool with the exact user_id from session.\n"
            "3. Wait for the authenticate_user result.\n"
            "4. If authentication SUCCESSFUL → IMMEDIATELY call switch_to_query. Make this switch without saying anything to the user.\n"
            "5. If authentication FAILS → Politely ask them to try again.\n"
            "6. After each tool call, always take the next action — never leave silence.\n\n"
            "POST-AUTHENTICATION RULES:\n"
            "- On SUCCESS: Do NOT speak to the user, do NOT say 'you are authenticated', do NOT congratulate.\n"
            "- On FAILURE: The authentication failed. Respond naturally and ask them to try again. Be conversational and helpful.\n"
            "- The QueryAgent will handle the welcome message after switching — you must remain silent.\n"
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
            "- Let QueryAgent speak first after switching.\n"
        )
    
    async def on_enter(self) -> None:
        """Initialize the authentication agent."""
        await super().on_enter()
        self.session.userdata.state = SessionState.AUTHENTICATING
        
        # Direct, natural greeting
        if self.user_name:
            greeting = f"Hey {self.user_name}! I'll need your four-digit security OTP code to get you into your account."
        else:
            greeting = "Hello! Please give me your four-digit security code so I can help you access your account."
        
        await self.session.generate_reply(instructions=f"Greeting: {greeting}")
        logger.info(f"AuthAgent started for user: {self.user_name}")
    
    @function_tool
    async def authenticate_user(self, context: RunContext) -> str:
        """Authenticate user with OTP code."""
        # This would integrate with your actual authentication system
        # For now, we'll simulate authentication
        logger.info(f"Authenticating user {self.user_id}")
        
        # Simulate authentication logic here
        # In a real implementation, this would call your auth service
        return "SUCCESS"
    
    @function_tool
    async def switch_to_query(self, context: RunContext) -> tuple:
        """Switch to QueryAgent after successful authentication."""
        from app.agents.query_agent import QueryAgent
        
        userdata = self.session.userdata
        userdata.is_authenticated = True
        
        # Simple context without exposing user ID to user
        query_context = (
            f"User {userdata.user_name} is authenticated. "
            f"Always use user_id '{userdata.user_id}' for all MCP calls. "
            "Be helpful and conversational. No special formatting."
        )
        
        logger.info(f"Successfully switching to QueryAgent for {userdata.user_name}")
        
        # Return with empty message - let QueryAgent handle the greeting
        return (
            QueryAgent(
                job_context=self.job_context,
                user_name=self.user_name,
                user_id=self.user_id,
                extra_instructions=query_context
            ),
            "",
        )