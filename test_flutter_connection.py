"""
Test script to verify Flutter client connection to LiveKit server.

This script helps you test if your Python LiveKit server is properly configured
to receive connections from your Flutter client.
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
    """Print connection information for Flutter client."""
    livekit_url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    
    logger.info("=== Flutter Connection Information ===")
    logger.info(f"LiveKit URL: {livekit_url}")
    logger.info(f"API Key: {api_key}")
    logger.info("Room Name: voice-assistant-room")
    logger.info("=====================================")
    
    print("\n" + "="*50)
    print("FLUTTER CLIENT CONFIGURATION")
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


def main():
    """Main test function."""
    logger.info("Testing Flutter connection setup...")
    
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


if __name__ == "__main__":
    main()