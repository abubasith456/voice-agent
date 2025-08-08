from __future__ import annotations

import os
from dotenv import load_dotenv
from loguru import logger

from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, RoomInputOptions
from livekit.agents import mcp as lk_mcp
from livekit.plugins import deepgram, openai, silero

try:
    # Prefer LiveKit OpenAI plugin Async client
    from livekit.plugins.openai import AsyncClient as LKAsyncClient  # type: ignore
except Exception:  # pragma: no cover
    LKAsyncClient = None  # type: ignore

from gocare.state import ConversationContext
from gocare.agents import MultiAgent


load_dotenv()


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()

    # Register your MCP server so the LLM can call its tools directly
    mcp_url = os.getenv("MCP_SERVER_URL", "").strip()
    fnc_ctx = None
    if mcp_url:
        mcp_server = lk_mcp.MCPServerHTTP(url=mcp_url)
        fnc_ctx = lk_mcp.FunctionContext(servers=[mcp_server])

    # Build LLM using AsyncClient (e.g., NVIDIA via OpenAI-compatible endpoint)
    llm_api_key = os.getenv("LLM_API_KEY", "").strip()
    llm_base_url = os.getenv("LLM_BASE_URL", "").strip()
    llm_model = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini").strip()

    if LKAsyncClient is None:
        # Fallback to default client if AsyncClient is unavailable
        llm = openai.LLM(model=llm_model)
    else:
        openai_client = LKAsyncClient(api_key=llm_api_key, base_url=llm_base_url)
        llm = openai.LLM(client=openai_client, model=llm_model)

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=llm,
        tts=deepgram.TTS(model="aura-asteria-en"),
        userdata=ConversationContext(),
        fnc_ctx=fnc_ctx,
    )

    await session.start(
        agent=MultiAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))