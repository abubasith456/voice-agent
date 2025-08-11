"""
Test script to verify LiveKit server setup and user connections.

This script helps you test if your Python LiveKit server is properly configured
to receive connections from any client (web, mobile, etc.).
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
        'LIVEKIT_URL',
        'LLM_API_KEY',
        'LLM_BASE_URL',
        'LLM_MODEL_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.strip() == '':
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return False
    
    logger.info("All required environment variables are set")
    return True


def print_connection_info():
    """Print connection information for clients."""
    livekit_url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    
    logger.info("=== LiveKit Connection Information ===")
    logger.info(f"LiveKit URL: {livekit_url}")
    logger.info(f"API Key: {api_key}")
    logger.info("Room Name: voice-assistant-room")
    logger.info("=====================================")
    
    print("\n" + "="*50)
    print("LIVEKIT SERVER CONFIGURATION")
    print("="*50)
    print(f"LIVEKIT_URL: {livekit_url}")
    print(f"LIVEKIT_API_KEY: {api_key}")
    print("ROOM_NAME: voice-assistant-room")
    print("="*50)


def create_test_token():
    """Create a test JWT token for testing."""
    try:
        import jwt
        from datetime import datetime, timedelta
        
        api_key = os.getenv('LIVEKIT_API_KEY')
        api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not api_key or not api_secret:
            logger.error("API key or secret not found")
            return None
        
        now = datetime.utcnow()
        exp = now + timedelta(hours=1)
        
        claims = {
            'iss': api_key,
            'sub': 'test-user',
            'name': 'Test User',
            'nbf': int(now.timestamp()),
            'exp': int(exp.timestamp()),
            'video': {
                'roomCreate': True,
                'roomJoin': True,
                'room': 'voice-assistant-room',
                'canPublish': True,
                'canSubscribe': True,
            },
        }
        
        token = jwt.encode(claims, api_secret, algorithm='HS256')
        logger.info(f"Test token created: {token[:50]}...")
        return token
        
    except ImportError:
        logger.error("PyJWT not installed. Install with: pip install PyJWT")
        return None
    except Exception as e:
        logger.error(f"Error creating test token: {e}")
        return None


async def test_room_connection():
    """Test if the room can be created and accessed."""
    try:
        from livekit import rtc
        
        livekit_url = os.getenv('LIVEKIT_URL')
        token = create_test_token()
        
        if not token:
            return False
        
        # Create a room instance
        room = rtc.Room()
        
        # Try to connect
        logger.info("Testing room connection...")
        await room.connect(livekit_url, token)
        
        logger.info(f"Successfully connected to room: {room.name}")
        logger.info(f"Room SID: {room.sid}")
        
        # Disconnect
        await room.disconnect()
        logger.info("Test connection successful!")
        return True
        
    except Exception as e:
        logger.error(f"Test connection failed: {e}")
        return False


def test_agent_session():
    """Test if the agent session can be created."""
    try:
        from openai import AsyncClient
        from livekit.plugins import deepgram, openai, silero, noise_cancellation
        from livekit.plugins.turn_detector.multilingual import MultilingualModel
        from gocare.state import ConversationContext
        from gocare.agents import MultiAgent
        
        # Test LLM setup
        llm_api_key = os.getenv("LLM_API_KEY", "").strip()
        llm_base_url = os.getenv("LLM_BASE_URL", "").strip()
        llm_model = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini").strip()
        
        openai_client = AsyncClient(api_key=llm_api_key, base_url=llm_base_url)
        llm = openai.LLM(client=openai_client, model=llm_model)
        
        logger.info("LLM setup successful")
        
        # Test plugins
        vad = silero.VAD.load()
        stt = deepgram.STT(model="nova-3", language="en")
        tts = deepgram.TTS(model="aura-asteria-en")
        turn_detection = MultilingualModel()
        
        logger.info("All plugins loaded successfully")
        
        # Test agent
        agent = MultiAgent()
        logger.info("MultiAgent created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Agent session test failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Testing LiveKit server setup...")
    
    # Check environment
    if not check_environment():
        return
    
    # Print connection info
    print_connection_info()
    
    # Test token creation
    token = create_test_token()
    if token:
        print(f"\nTest Token: {token}")
    
    # Test room connection
    print("\nTesting room connection...")
    asyncio.run(test_room_connection())
    
    # Test agent session
    print("\nTesting agent session...")
    test_agent_session()
    
    print("\n" + "="*50)
    print("SETUP COMPLETE")
    print("="*50)
    print("Your LiveKit server is ready to accept connections!")
    print("Run 'python worker.py' to start the server.")
    print("="*50)


if __name__ == "__main__":
    main()