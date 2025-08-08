from __future__ import annotations

from dotenv import load_dotenv
from loguru import logger

from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, RoomInputOptions
from livekit.plugins import deepgram, openai, silero

from gocare.state import ConversationContext
from gocare.agents.greeting_agent import GreetingAgent


load_dotenv()


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()

    session = AgentSession[ConversationContext](
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),  # Point OPENAI_BASE_URL to OpenRouter to use OpenRouter
        tts=deepgram.TTS(model="aura-asteria-en"),
        userdata=ConversationContext(),
    )

    await session.start(
        agent=GreetingAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))