# Updated LiveKit Python Server

The Python server has been updated to properly handle user connections, fix the async callback error, provide personalized greetings using user metadata from Flutter, and implement a new user_id and OTP authentication flow.

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

### 4. **New Authentication Flow** 🔐 **NEW**
- **Old**: Mobile number authentication
- **New**: User ID + OTP authentication
- Two-step process: Request OTP → Verify OTP
- Enhanced security with OTP expiration and attempt limits

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
- ✅ **NEW**: Updated authentication flow for user_id + OTP
- ✅ **NEW**: Improved prompts for banking assistant

### `gocare/agents/main_agent.py`
- ✅ **NEW**: Enhanced logging for user name usage
- ✅ **NEW**: Better handling of personalized greetings

### `gocare/state.py`
- ✅ **NEW**: Added OTP_PENDING state
- ✅ **NEW**: Track OTP request status and pending user_id

### `mcp_server/app.py`
- ✅ **NEW**: Updated authenticate_user to handle user_id + OTP
- ✅ **NEW**: OTP generation and verification
- ✅ **NEW**: OTP expiration (5 minutes) and attempt limits (3 attempts)

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

## New Authentication Flow

### Step 1: Request OTP
```
User: "u001"
Assistant: "OTP sent to your registered mobile number. Please provide the 6-digit OTP."
```

### Step 2: Verify OTP
```
User: "123456"
Assistant: "Hello John, how can I assist you today?"
```

### User ID Format
- Must be exactly 3 characters starting with 'u' followed by 3 digits
- Examples: `u001`, `u002`, `u003`
- Voice: Read as "u zero zero one"

### OTP Format
- Must be exactly 6 digits
- Examples: `123456`, `000000`, `999999`
- Voice: Read as individual digits

## Testing

### 1. Test Your Setup
```bash
python test_flutter_connection.py
```

### 2. Test Metadata Extraction
```bash
python test_user_metadata.py
```

### 3. Test Authentication Flow
```bash
python test_authentication_flow.py
```

### 4. Start the Server
```bash
python worker.py
```

### 5. Check Logs
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
- ✅ **User ID + OTP Authentication**: Enhanced security flow 🔐
- ✅ **OTP Management**: Generation, verification, expiration 🔐
- ✅ **Error Handling**: Robust error handling throughout
- ✅ **Comprehensive Logging**: Track all events and issues

## Authentication Security Features

- 🔐 **OTP Generation**: 6-digit random OTP
- 🔐 **OTP Expiration**: 5-minute validity period
- 🔐 **Attempt Limits**: Maximum 3 failed attempts
- 🔐 **User ID Validation**: Strict format validation
- 🔐 **Secure Storage**: Temporary OTP storage (use Redis in production)

## Personalized Greetings Flow

1. **Flutter Client**: Sets metadata with user info
2. **Python Server**: Extracts metadata on connection
3. **MultiAgent**: "Welcome John! Please provide your user ID to continue."
4. **Authentication**: User provides user_id → OTP → Verification
5. **GreetingAgent**: "Hello John, how can I assist you today?"
6. **MainAgent**: Continues using user name throughout session

### Example Conversation Flow
```
Assistant: "Welcome John! Please provide your user ID to continue."
User: "u zero zero one"
Assistant: "OTP sent to your registered mobile number. Please provide the 6-digit OTP."
User: "one two three four five six"
Assistant: "Hello John, how can I assist you today?"
```

## Usage

The server will now:
1. **Detect user connections** and extract metadata
2. **Send personalized welcome messages** using the user's name
3. **Handle user_id + OTP authentication** with enhanced security
4. **Process data messages** from users
5. **Handle commands** like start/stop conversation
6. **Integrate with your agent system** for voice processing
7. **Provide personalized greetings** throughout the conversation

Your existing Flutter code should now work properly with this updated server and provide secure, personalized user experiences! 🎉🔐