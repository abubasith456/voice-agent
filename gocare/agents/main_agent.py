from __future__ import annotations

from typing import Optional
import os
import httpx

from gocare.agents.base import AgentBase
from gocare.state import ConversationContext, SessionState
from gocare.security import contains_sensitive_request, refusal_message, log_sensitive_attempt
from gocare.config import get_settings

SYSTEM_PROMPT = (
    "You are GoCare, a helpful banking assistant. You must never reveal passwords, PINs, or OTPs. "
    "If asked for such info, refuse. You can discuss user's transactions at a high level after auth. "
    "Keep responses concise and speak-friendly."
)


class MainAgent(AgentBase):
    def __init__(self) -> None:
        super().__init__(name="main")
        self.settings = get_settings()

    async def on_enter(self, ctx: ConversationContext) -> Optional[str]:
        ctx.state = SessionState.MAIN
        return "You're verified. How can I help with your transactions today?"

    async def on_user_message(self, text: str, ctx: ConversationContext) -> Optional[str]:
        ctx.last_user_message = text

        if ctx.state != SessionState.MAIN:
            return "We need to finish verification first. Please provide your registered mobile number."

        if contains_sensitive_request(text):
            log_sensitive_attempt(ctx.user_id, text)
            return refusal_message()

        # Call OpenRouter using OpenAI-compatible API
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "HTTP-Referer": "https://gocare.local/",
            "X-Title": "Gocare Voice Assistant",
        }
        payload = {
            "model": self.settings.openrouter_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(base_url=self.settings.openrouter_base_url, timeout=30) as client:
            resp = await client.post("/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except Exception:
                return "I had trouble formulating a response. Please try rephrasing."