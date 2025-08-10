# Updated LiveKit Python Server

The Python server has been updated to properly handle user connections and fix the async callback error.

## What Was Fixed

### 1. **Async Callback Error**
- **Problem**: LiveKit's `.on()` method expects synchronous callbacks, not async ones
- **Solution**: Use synchronous callbacks that create asyncio tasks for async operations

### 2. **User Connection Handling**
- Added proper event handlers for participant connections
- Added data message processing
- Added welcome message functionality
- Added comprehensive logging

## Key Changes

### `worker.py`
- ✅ Fixed async callback registration
- ✅ Added participant connection/disconnection handlers
- ✅ Added data message processing
- ✅ Added welcome message system
- ✅ Enhanced logging and error handling

### Event Handler Pattern
```python
# ✅ CORRECT: Synchronous callback with asyncio task
def handle_participant_connected(participant):
    asyncio.create_task(process_participant_connection(participant))

ctx.room.on("participant_connected", handle_participant_connected)
```

## Testing

### 1. Test Your Setup
```bash
python test_flutter_connection.py
```

### 2. Start the Server
```bash
python worker.py
```

### 3. Check Logs
Look for these messages when users connect:
```
Room 'voice-assistant-room' is ready to accept connections
User connected: user-identity
Participant SID: PA_xxxxxxxx
Sent welcome message to user-identity
```

## Environment Variables

Make sure your `.env` file has:
```bash
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_URL=wss://your-livekit-server.com
LLM_API_KEY=your_llm_key
LLM_BASE_URL=your_llm_url
LLM_MODEL_NAME=gpt-4o-mini
```

## Features

- ✅ **User Connection Detection**: Know when users join/leave
- ✅ **Data Communication**: Send/receive messages with users
- ✅ **Welcome Messages**: Automatically greet new users
- ✅ **Error Handling**: Robust error handling throughout
- ✅ **Comprehensive Logging**: Track all events and issues

## Usage

The server will now:
1. **Detect user connections** and log participant information
2. **Send welcome messages** to new users
3. **Process data messages** from users
4. **Handle commands** like start/stop conversation
5. **Integrate with your agent system** for voice processing

Your existing Flutter code should now work properly with this updated server!