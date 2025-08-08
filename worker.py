from __future__ import annotations

import os
from dotenv import load_dotenv
from loguru import logger

from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, RoomInputOptions
from livekit.agents import mcp as lk_mcp
from livekit.plugins import deepgram, openai, silero

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

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),  # set OPENAI_BASE_URL to point to OpenRouter
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