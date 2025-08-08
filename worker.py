from __future__ import annotations

import asyncio
import os
from loguru import logger

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins.deepgram import DeepgramSTT, DeepgramTTS

from gocare.config import get_settings
from gocare.manager import MultiAgentManager


async def entrypoint(ctx: JobContext) -> None:
    settings = get_settings()

    stt = DeepgramSTT(api_key=settings.deepgram_api_key, model="nova-2")
    tts = DeepgramTTS(api_key=settings.deepgram_api_key, voice="aura-asteria-en")

    manager = MultiAgentManager()

    assistant = VoiceAssistant(
        stt=stt,
        tts=tts,
        vad_enabled=True,
        allow_interruptions=True,
    )

    await assistant.start(ctx)

    # Send initial greeting
    initial = await manager.start()
    await assistant.say(initial)

    @assistant.on("transcript")
    async def on_transcript(text: str) -> None:
        try:
            reply = await manager.handle_user_text(text)
            if reply:
                await assistant.say(reply)
        except Exception as e:
            logger.exception("Error handling transcript: {}", e)
            await assistant.say("Sorry, I ran into an error.")


if __name__ == "__main__":
    cli.run_app(entrypoint, WorkerOptions(auto_subscribe=AutoSubscribe.AUDIO_ONLY))