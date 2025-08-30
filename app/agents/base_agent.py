from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from livekit.agents import Agent, JobContext


class BaseAgent(Agent, ABC):
    """Abstract base class for all agents in the system."""
    
    def __init__(
        self, 
        job_context: JobContext,
        user_name: Optional[str] = None,
        user_id: Optional[str] = None,
        extra_instructions: str = ""
    ) -> None:
        self.job_context = job_context
        self.user_name = user_name
        self.user_id = user_id
        
        instructions = self.get_base_instructions() + extra_instructions
        super().__init__(instructions=instructions)
    
    @abstractmethod
    def get_base_instructions(self) -> str:
        """Return the base instructions for this agent type."""
        pass
    
    async def on_enter(self) -> None:
        """Called when the agent enters the session."""
        if hasattr(self.session, 'userdata'):
            self.session.userdata.user_name = self.user_name
            self.session.userdata.user_id = self.user_id