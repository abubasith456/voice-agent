from __future__ import annotations

import os
from dotenv import load_dotenv
from loguru import logger

from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, RoomInputOptions
from livekit.agents import mcp  # import as mcp for clarity
from livekit.plugins import deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

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

    # Register MCP server(s) so the LLM can choose tools directly
    mcp_url = os.getenv("MCP_SERVER_URL", "").strip()
    mcp_servers = [mcp.MCPServerHTTP(url=mcp_url)] if mcp_url else None

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=llm,
        tts=deepgram.TTS(model="aura-asteria-en"),
        userdata=ConversationContext(),
        turn_detection=MultilingualModel(),
        mcp_servers=mcp_servers,
    )

    await session.start(
        agent=MultiAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))