from __future__ import annotations

from loguru import logger
from livekit.agents import RunContext, function_tool

from app.agents.base_agent import BaseAgent
from app.state import SessionState


class QueryAgent(BaseAgent):
    """Handles user queries and account details after authentication."""
    
    def get_base_instructions(self) -> str:
        return (
            "You're a helpful bank representative assisting customers with their account information.\n\n"
            "What you can help with:\n"
            "- Account details and personal info (use get_user_info)\n"
            "- Bill amounts and payment info (use get_user_bill)\n"
            "- Contact details on file (use get_user_contact)\n"
            "- Recent login activity (use get_user_last_login)\n"
            "- Connect to human support (use switch_to_helpline)\n\n"
            "SECURITY RESPONSE GUIDELINES:\n"
            "When customers ask about passwords, PINs, SSNs, or other sensitive information:\n"
            "- Express understanding and empathy naturally\n"
            "- Explain security reasons in your own words (vary your explanation each time)\n"
            "- Always offer to connect them with helpline for secure assistance\n"
            "- Use phrases like 'I understand', 'I get it', 'I totally understand why you need that'\n"
            "- Vary your explanations - don't repeat the same security explanation\n"
            "- End by asking if they'd like to be connected to our support specialists\n"
            "- Sound genuinely helpful, not robotic\n\n"
            "RESPONSE VARIETY RULES:\n"
            "- Never give identical responses to similar requests\n"
            "- Use different phrases each time: 'I understand', 'I get why you need that', 'That makes sense'\n"
            "- Vary security explanations: 'for your protection', 'to keep your account secure', 'for security reasons'\n"
            "- Mix up connection offers: 'Would you like me to connect you?', 'Should I get you over to our team?', 'Can I transfer you to someone who can help?'\n\n"
            "CONVERSATION RULES:\n"
            "- Talk like you're having a normal phone conversation\n"
            "- Use the customer's name occasionally, not every sentence\n"
            "- Keep responses conversational and brief\n"
            "- Never mention technical terms, tools, or systems\n"
            "- Present information naturally, like you already know it\n"
            "- Be empathetic and helpful, even when declining requests\n"
            "- Generate fresh, natural responses each time\n\n"
            "FORBIDDEN FORMATTING:\n"
            "- No asterisks, hashtags, brackets, or special symbols\n"
            "- No markdown, bold, or italic text\n"
            "- Write in flowing, natural sentences\n\n"
            "SENSITIVE DATA HANDLING:\n"
            "- Passwords, PINs, SSNs, account numbers: Cannot access for security\n"
            "- Always acknowledge their need first\n"
            "- Explain why you can't help with that specific request\n"
            "- Offer helpline connection as the solution\n"
            "- Keep it conversational and understanding\n"
        )
    
    async def on_enter(self) -> None:
        """Initialize the query agent."""
        await super().on_enter()
        self.session.userdata.state = SessionState.MAIN
        
        # Simple success message
        user_name = self.session.userdata.user_name
        if user_name:
            welcome = f"You have successfully authenticated, {user_name}. How can I help you with your account today?"
        else:
            welcome = "You have successfully authenticated. How can I help you with your account today?"
        
        await self.session.generate_reply(instructions=welcome)
        logger.info(f"QueryAgent started for user: {user_name}")
    
    @function_tool
    async def get_user_info(self, context: RunContext) -> str:
        """Get user account information."""
        logger.info(f"Getting user info for {self.user_id}")
        # This would integrate with your actual user info service
        return f"Account information for user {self.user_id}"
    
    @function_tool
    async def get_user_bill(self, context: RunContext) -> str:
        """Get user bill information."""
        logger.info(f"Getting bill info for {self.user_id}")
        # This would integrate with your actual billing service
        return f"Bill information for user {self.user_id}"
    
    @function_tool
    async def get_user_contact(self, context: RunContext) -> str:
        """Get user contact information."""
        logger.info(f"Getting contact info for {self.user_id}")
        # This would integrate with your actual contact service
        return f"Contact information for user {self.user_id}"
    
    @function_tool
    async def get_user_last_login(self, context: RunContext) -> str:
        """Get user's last login information."""
        logger.info(f"Getting last login info for {self.user_id}")
        # This would integrate with your actual login service
        return f"Last login information for user {self.user_id}"
    
    @function_tool
    async def switch_to_helpline(self, context: RunContext) -> tuple:
        """Connect customer to human support."""
        from app.agents.helpline_agent import HelplineAgent
        
        userdata = self.session.userdata
        
        helpline_context = (
            f"You're a human support specialist helping {userdata.user_name}. "
            f"Their account ID is {userdata.user_id}. "
            "Be helpful and professional. Talk naturally like a real person. "
            "If they want to end the call, use the end_session function. "
            "Never use special formatting or mention technical processes."
        )
        
        # First send the connecting message
        await self.session.generate_reply(
            instructions=f"Alright {userdata.user_name}, let me get you over to one of our specialists."
        )
        
        return (
            HelplineAgent(
                job_context=self.job_context,
                user_name=self.user_name,
                user_id=self.user_id,
                extra_instructions=helpline_context
            ),
            ""
        )