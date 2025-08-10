from __future__ import annotations

import os
import asyncio
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

from gocare.state import ConversationContext
from gocare.agents import MultiAgent


load_dotenv()


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()
    
    # Set up room event handlers to properly handle Flutter client connections
    def handle_participant_connected(participant):
        """Handle when a Flutter client connects to the room."""
        asyncio.create_task(process_participant_connection(participant))
    
    def handle_participant_disconnected(participant):
        """Handle when a Flutter client disconnects from the room."""
        asyncio.create_task(process_participant_disconnection(participant))
    
    def handle_data_received(data_packet, participant):
        """Handle data messages from Flutter client."""
        asyncio.create_task(process_data_message(data_packet, participant))
    
    # Register event handlers
    ctx.room.on("participant_connected", handle_participant_connected)
    ctx.room.on("participant_disconnected", handle_participant_disconnected)
    ctx.room.on("data_received", handle_data_received)
    
    logger.info(f"Room '{ctx.room.name}' is ready to accept connections")
    logger.info(f"Room SID: {ctx.room.sid}")

    # Build LLM using AsyncClient (e.g., NVIDIA via OpenAI-compatible endpoint)
    llm_api_key = os.getenv("LLM_API_KEY", "").strip()
    llm_base_url = os.getenv("LLM_BASE_URL", "").strip()
    llm_model = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini").strip()

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

    await session.start(
        agent=MultiAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            text_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


async def process_participant_connection(participant):
    """Process when a Flutter client connects."""
    try:
        logger.info(f"Flutter client connected: {participant.identity}")
        logger.info(f"Participant SID: {participant.sid}")
        
        # Log participant attributes (from Flutter client)
        if participant.metadata:
            logger.info(f"Participant metadata: {participant.metadata}")
        
        # Check if participant has audio tracks
        audio_tracks = [track for track in participant.audio_tracks.values() if track.is_subscribed]
        logger.info(f"Participant has {len(audio_tracks)} audio tracks")
        
        # Send welcome message to the client
        await send_welcome_message(participant)
        
    except Exception as e:
        logger.error(f"Error processing participant connection: {e}")


async def process_participant_disconnection(participant):
    """Process when a Flutter client disconnects."""
    try:
        logger.info(f"Flutter client disconnected: {participant.identity}")
        # Clean up any resources associated with this participant
    except Exception as e:
        logger.error(f"Error processing participant disconnection: {e}")


async def process_data_message(data_packet, participant):
    """Process data messages from Flutter client."""
    try:
        logger.info(f"Received data from {participant.identity}: {data_packet.data}")
        
        # Handle different types of messages
        if isinstance(data_packet.data, dict):
            message_type = data_packet.data.get('type')
            if message_type == 'text':
                await handle_text_message(data_packet.data.get('text', ''), participant)
            elif message_type == 'command':
                await handle_command_message(data_packet.data.get('command', ''), participant)
        
    except Exception as e:
        logger.error(f"Error processing data message: {e}")


async def send_welcome_message(participant):
    """Send a welcome message to the connected Flutter client."""
    try:
        welcome_data = {
            'type': 'welcome',
            'message': 'Welcome to the voice assistant! I\'m ready to help you.',
            'timestamp': asyncio.get_event_loop().time()
        }
        
        # Send data to the specific participant
        await participant.send_data(
            data=welcome_data,
            topic='system'
        )
        logger.info(f"Sent welcome message to {participant.identity}")
        
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")


async def handle_text_message(text: str, participant):
    """Handle text messages from Flutter client."""
    try:
        logger.info(f"Processing text message from {participant.identity}: {text}")
        
        # Here you can integrate with your agent system
        # For now, just echo back
        response_data = {
            'type': 'response',
            'text': f'You said: {text}',
            'timestamp': asyncio.get_event_loop().time()
        }
        
        await participant.send_data(
            data=response_data,
            topic='chat'
        )
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}")


async def handle_command_message(command: str, participant):
    """Handle command messages from Flutter client."""
    try:
        logger.info(f"Processing command from {participant.identity}: {command}")
        
        # Handle different commands
        if command == 'start_conversation':
            # Start the voice conversation
            pass
        elif command == 'stop_conversation':
            # Stop the voice conversation
            pass
        
        # Send command acknowledgment
        response_data = {
            'type': 'command_response',
            'command': command,
            'status': 'processed',
            'timestamp': asyncio.get_event_loop().time()
        }
        
        await participant.send_data(
            data=response_data,
            topic='system'
        )
        
    except Exception as e:
        logger.error(f"Error handling command message: {e}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
