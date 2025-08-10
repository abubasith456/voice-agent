# Updated LiveKit Python Server

The Python server has been updated to properly handle user connections, fix the async callback error, and provide personalized greetings using user metadata from Flutter.

## What Was Fixed

### 1. **Async Callback Error**
- **Problem**: LiveKit's `.on()` method expects synchronous callbacks, not async ones
- **Solution**: Use synchronous callbacks that create asyncio tasks for async operations

### 2. **User Connection Handling**
- Added proper event handlers for participant connections
- Added data message processing
- Added welcome message functionality
- Added comprehensive logging

### 3. **Personalized User Greetings** ✨ **NEW**
- Extract user metadata from Flutter client
- Parse JSON metadata containing `userId` and `userName`
- Set user information in conversation context
- Provide personalized greetings using the user's name

## Key Changes

### `worker.py`
- ✅ Fixed async callback registration
- ✅ Added participant connection/disconnection handlers
- ✅ Added data message processing
- ✅ Added personalized welcome message system
- ✅ **NEW**: Extract and use user metadata from Flutter
- ✅ Enhanced logging and error handling

### `gocare/agents/multi_agent.py`
- ✅ **NEW**: Check for existing user name from Flutter metadata
- ✅ **NEW**: Provide personalized initial greetings
- ✅ **NEW**: Use existing user name during authentication flow

### `gocare/agents/main_agent.py`
- ✅ **NEW**: Enhanced logging for user name usage
- ✅ **NEW**: Better handling of personalized greetings

### Event Handler Pattern
```python
# ✅ CORRECT: Synchronous callback with asyncio task
def handle_participant_connected(participant):
    asyncio.create_task(process_participant_connection(participant, ctx))

ctx.room.on("participant_connected", handle_participant_connected)
```

## Flutter Integration

### Flutter Code (Your existing code)
```dart
participant.setMetadata(
  '{"userId": "${widget.selectedUser.id}", "userName": "${widget.selectedUser.name}"}',
);
```

### Python Server Processing
```python
# Extract user metadata from Flutter client
if participant.metadata:
    metadata = json.loads(participant.metadata)
    user_id = metadata.get('userId')
    user_name = metadata.get('userName')
    
    # Set in conversation context
    ctx.session.userdata.user_id = user_id
    ctx.session.userdata.user_name = user_name
```

## Testing

### 1. Test Your Setup
```bash
python test_flutter_connection.py
```

### 2. Test Metadata Extraction
```bash
python test_user_metadata.py
```

### 3. Start the Server
```bash
python worker.py
```

### 4. Check Logs
Look for these messages when users connect:
```
Room 'voice-assistant-room' is ready to accept connections
User connected: user-identity
Participant metadata: {"userId": "user123", "userName": "John Doe"}
Extracted user info - ID: user123, Name: John Doe
Set user data in conversation context: John Doe (user123)
Sent personalized welcome message to user-identity: John Doe
Using personalized greeting for user: John Doe
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
- ✅ **Personalized Welcome Messages**: Greet users by name ✨
- ✅ **User Metadata Extraction**: Parse Flutter client metadata ✨
- ✅ **Error Handling**: Robust error handling throughout
- ✅ **Comprehensive Logging**: Track all events and issues

## Personalized Greetings Flow

1. **Flutter Client**: Sets metadata with user info
2. **Python Server**: Extracts metadata on connection
3. **MultiAgent**: Uses user name for initial greeting
4. **GreetingAgent**: Personalized welcome after authentication
5. **MainAgent**: Continues using user name throughout session

### Example Greetings
- **With User Name**: "Welcome John! Please say your registered mobile number."
- **Without User Name**: "Welcome. Please say your registered mobile number."

## Usage

The server will now:
1. **Detect user connections** and extract metadata
2. **Send personalized welcome messages** using the user's name
3. **Process data messages** from users
4. **Handle commands** like start/stop conversation
5. **Integrate with your agent system** for voice processing
6. **Provide personalized greetings** throughout the conversation

Your existing Flutter code should now work properly with this updated server and provide personalized user experiences!