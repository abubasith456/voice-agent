from __future__ import annotations

import os
import asyncio
import json
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncClient

from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    AgentSession,
    RoomInputOptions,
)
from livekit.agents import mcp  # import as mcp for clarity
from livekit.plugins import deepgram, openai, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from app.state import ConversationContext
from app.agents.multi_agent_new import MultiAgent
from app.agents.basic_agent import BasicAgent


load_dotenv()


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()

    participant = await ctx.wait_for_participant()
    logger.info(f"Participant metadata: {participant.metadata}")

    user_name = None
    user_id = None
    is_auth_based = False

    if participant.metadata:
        try:
            metadata = json.loads(participant.metadata)
            logger.info(f"Participant metadata loaded: {metadata}")

            user_name = metadata.get("userName", "").strip()
            user_id = metadata.get("userId", "").strip()
            is_auth_based = metadata.get("is_auth_based", False)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse participant metadata: {e}")
            metadata = {}

    logger.info(f"Room '{ctx.room.name}' is ready to accept connections")
    logger.info(f"Room SID: {ctx.room.sid}")
    logger.info(f"User name: {user_name}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Auth-based flow: {is_auth_based}")

    # Build LLM using AsyncClient (e.g., NVIDIA via OpenAI-compatible endpoint)
    llm_api_key = os.getenv("LLM_API_KEY", "").strip()
    llm_base_url = os.getenv("LLM_BASE_URL", "").strip()
    llm_model = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini").strip()

    logger.info(f"LLM Model Name: {llm_model}")

    openai_client = AsyncClient(api_key=llm_api_key, base_url=llm_base_url)
    llm = openai.LLM(client=openai_client, model=llm_model)

    # Register MCP server(s) so the LLM can choose tools directly
    mcp_url = os.getenv("MCP_SERVER_URL", "").strip()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=llm,
        tts=deepgram.TTS(model="aura-asteria-en"),
        userdata=ConversationContext(),
        turn_detection=MultilingualModel(),
        mcp_servers=([mcp.MCPServerHTTP(url=mcp_url)] if mcp_url else []),
    )

    # Choose agent based on metadata
    if is_auth_based:
        logger.info("Starting MultiAgent flow (auth-based)")
        agent = MultiAgent(
            job_context=ctx,
            user_name=user_name,
            user_id=user_id
        )
    else:
        logger.info("Starting BasicAgent flow (non-auth-based)")
        agent = BasicAgent(
            job_context=ctx,
            user_name=user_name,
            user_id=user_id
        )

    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            text_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))