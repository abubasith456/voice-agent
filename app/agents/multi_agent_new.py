from __future__ import annotations

from typing import Optional
from loguru import logger
from livekit.agents import JobContext

from app.agents.base_agent import BaseAgent
from app.agents.auth_agent import AuthAgent
from app.agents.query_agent import QueryAgent
from app.agents.helpline_agent import HelplineAgent
from app.state import SessionState


class MultiAgent(BaseAgent):
    """Orchestrator agent that manages the flow between AuthAgent, QueryAgent, and HelplineAgent."""
    
    def __init__(
        self,
        job_context: JobContext,
        user_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        # Initialize sub-agents (composition, not inheritance)
        self.auth_agent = AuthAgent(
            job_context=job_context,
            user_name=user_name,
            user_id=user_id
        )
        
        self.query_agent = QueryAgent(
            job_context=job_context,
            user_name=user_name,
            user_id=user_id
        )
        
        self.helpline_agent = HelplineAgent(
            job_context=job_context,
            user_name=user_name,
            user_id=user_id
        )
        
        # Start with auth agent
        super().__init__(
            job_context=job_context,
            user_name=user_name,
            user_id=user_id,
            extra_instructions="You are the orchestrator. Start with authentication."
        )
        
        self.current_agent = self.auth_agent
        logger.info(f"MultiAgent initialized for user: {user_name}")
    
    def get_base_instructions(self) -> str:
        return (
            "You are the MultiAgent orchestrator that manages the conversation flow.\n\n"
            "AGENT FLOW:\n"
            "1. Start with AuthAgent for authentication\n"
            "2. Switch to QueryAgent after successful authentication\n"
            "3. Switch to HelplineAgent when human support is needed\n\n"
            "RESPONSIBILITIES:\n"
            "- Route user input to the appropriate sub-agent\n"
            "- Manage transitions between agents\n"
            "- Maintain conversation context across agents\n"
            "- Handle agent switching logic\n\n"
            "CURRENT STATE:\n"
            "- Always delegate to the current active agent\n"
            "- Do not process user input directly\n"
            "- Focus on orchestration and routing\n"
        )
    
    async def on_enter(self) -> None:
        """Initialize the multi-agent system."""
        await super().on_enter()
        self.session.userdata.state = SessionState.AUTHENTICATING
        
        # Start with the auth agent
        await self.current_agent.on_enter()
        logger.info("MultiAgent started with AuthAgent")
    
    async def handle_input(self, text: str) -> str:
        """Route user input to the appropriate sub-agent."""
        logger.info(f"MultiAgent routing input to {type(self.current_agent).__name__}")
        
        # Delegate to current agent
        if isinstance(self.current_agent, AuthAgent):
            return await self._handle_auth_input(text)
        elif isinstance(self.current_agent, QueryAgent):
            return await self._handle_query_input(text)
        elif isinstance(self.current_agent, HelplineAgent):
            return await self._handle_helpline_input(text)
        else:
            logger.error(f"Unknown agent type: {type(self.current_agent)}")
            return "I'm sorry, there was an error. Please try again."
    
    async def _handle_auth_input(self, text: str) -> str:
        """Handle input when AuthAgent is active."""
        # Check if authentication was successful
        if self.session.userdata.is_authenticated:
            # Switch to QueryAgent
            self.current_agent = self.query_agent
            await self.current_agent.on_enter()
            return "Authentication successful. How can I help you with your account?"
        
        # Continue with auth agent
        return await self.current_agent.handle_input(text)
    
    async def _handle_query_input(self, text: str) -> str:
        """Handle input when QueryAgent is active."""
        # Check if helpline is requested
        if "helpline" in text.lower() or "human" in text.lower() or "support" in text.lower():
            # Switch to HelplineAgent
            self.current_agent = self.helpline_agent
            await self.current_agent.on_enter()
            return "Connecting you to our support specialist."
        
        # Continue with query agent
        return await self.current_agent.handle_input(text)
    
    async def _handle_helpline_input(self, text: str) -> str:
        """Handle input when HelplineAgent is active."""
        # Check if session should end
        if any(phrase in text.lower() for phrase in ["goodbye", "end", "bye", "logout"]):
            # Reset to AuthAgent for new session
            self.current_agent = self.auth_agent
            self.session.userdata.is_authenticated = False
            await self.current_agent.on_enter()
            return "Session ended. Please authenticate again for a new session."
        
        # Continue with helpline agent
        return await self.current_agent.handle_input(text)
    
    def switch_to_auth(self) -> None:
        """Switch back to authentication agent."""
        self.current_agent = self.auth_agent
        self.session.userdata.is_authenticated = False
        self.session.userdata.state = SessionState.AUTHENTICATING
        logger.info("Switched to AuthAgent")
    
    def switch_to_query(self) -> None:
        """Switch to query agent."""
        self.current_agent = self.query_agent
        self.session.userdata.state = SessionState.MAIN
        logger.info("Switched to QueryAgent")
    
    def switch_to_helpline(self) -> None:
        """Switch to helpline agent."""
        self.current_agent = self.helpline_agent
        self.session.userdata.state = SessionState.HELPLINE
        logger.info("Switched to HelplineAgent")