from __future__ import annotations

import os
from typing import Any, AsyncIterator
import httpx
from pydantic import BaseModel


class MCPSettings(BaseModel):
    base_url: str
    api_key: str | None = None
    http_prefix: str = "/mcp"

    @staticmethod
    def from_env() -> "MCPSettings":
        return MCPSettings(
            base_url=os.getenv("MCP_SERVER_URL", "").rstrip("/"),
            api_key=os.getenv("MCP_API_KEY"),
            http_prefix=os.getenv("MCP_HTTP_PREFIX", "/mcp"),
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

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if not self.settings.base_url:
            raise RuntimeError("MCP_SERVER_URL is not configured")
        url = f"{self.settings.base_url}{self.settings.http_prefix}/tools/call"
        try:
            resp = await self._client.post(url, headers=self._headers(), json={
                "name": name,
                "arguments": arguments,
            })
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            # try fallback direct endpoint if server didn't mount /mcp
            fallback = f"{self.settings.base_url}/{name}"
            r2 = await self._client.post(fallback, headers=self._headers(), json=arguments)
            r2.raise_for_status()
            return r2.json()

    async def authenticate_mobile(self, mobile: str) -> tuple[bool, str | None, str | None]:
        """Return (verified, user_id, name)."""
        if not self.settings.base_url:
            digits = [c for c in mobile if c.isdigit()]
            ok = len(digits) >= 10
            return ok, (f"user:{''.join(digits)[-4:]}" if ok else None), ("Demo User" if ok else None)
        data = await self._call_tool("authenticate_user", {"mobile_number": mobile})
        # FastMCP returns the tool's return value directly
        if isinstance(data, dict) and data.get("status") == "success":
            return True, data.get("user_id"), data.get("name")
        return False, None, None

    async def get_user_info(self, user_id: str) -> dict[str, Any]:
        if not self.settings.base_url:
            # demo data
            return {
                "name": "Demo User",
                "dob": "1990-01-01",
                "transactions": "[{\"date\":\"2025-06-28\",\"merchant\":\"Coffee House\",\"amount\":-4.75}]",
            }
        data = await self._call_tool("get_user_info", {"user_id": user_id})
        return data

    async def aclose(self) -> None:
        await self._client.aclose()