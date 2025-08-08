from __future__ import annotations

import os
from typing import Any, AsyncIterator
import httpx
from pydantic import BaseModel


class MCPSettings(BaseModel):
    base_url: str
    api_key: str | None = None

    @staticmethod
    def from_env() -> "MCPSettings":
        return MCPSettings(
            base_url=os.getenv("MCP_SERVER_URL", "").rstrip("/"),
            api_key=os.getenv("MCP_API_KEY"),
        )


class MCPClient:
    def __init__(self, settings: MCPSettings | None = None) -> None:
        self.settings = settings or MCPSettings.from_env()
        self._client = httpx.AsyncClient(timeout=30)

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers

    async def authenticate_mobile(self, mobile: str) -> tuple[bool, str | None]:
        if not self.settings.base_url:
            # Fallback demo behavior when MCP is not configured
            digits = [c for c in mobile if c.isdigit()]
            ok = len(digits) >= 10
            return ok, (f"user:{''.join(digits)[-4:]}" if ok else None)
        url = f"{self.settings.base_url}/authenticate"
        resp = await self._client.post(url, headers=self._headers(), json={"mobile": mobile})
        resp.raise_for_status()
        data = resp.json()
        return bool(data.get("verified")), data.get("user_id")

    async def stream_query(self, user_id: str, query: str) -> AsyncIterator[str]:
        if not self.settings.base_url:
            # Fallback demo: single chunk
            yield "For demo purposes, I cannot access live data."
            return
        url = f"{self.settings.base_url}/query"
        async with self._client.stream("POST", url, headers=self._headers(), json={"user_id": user_id, "query": query}) as r:
            r.raise_for_status()
            async for chunk in r.aiter_text():
                if chunk:
                    yield chunk

    async def aclose(self) -> None:
        await self._client.aclose()