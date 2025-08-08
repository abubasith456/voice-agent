from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger

from gocare.state import ConversationContext


class AgentBase(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    async def on_user_message(self, text: str, ctx: ConversationContext) -> Optional[str]:
        ...

    async def on_enter(self, ctx: ConversationContext) -> Optional[str]:
        logger.debug("Entering agent {} with state {}", self.name, ctx.state)
        return None

    async def on_exit(self, ctx: ConversationContext) -> None:
        logger.debug("Exiting agent {} with state {}", self.name, ctx.state)