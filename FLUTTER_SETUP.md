# Flutter to Python LiveKit Connection Setup

This guide explains how to connect your Flutter app to the Python LiveKit voice assistant server.

## Prerequisites

1. **Python Server Running**: Make sure your Python LiveKit server is running
2. **Environment Variables**: Configure your `.env` file with LiveKit credentials
3. **Flutter Dependencies**: Add required packages to your Flutter project

## Environment Setup

### 1. Python Server Environment Variables

Create a `.env` file in your Python project root:

```bash
# LiveKit Configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.com

# LLM Configuration
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://your-llm-endpoint.com/v1
LLM_MODEL_NAME=gpt-4o-mini

# MCP Server (optional)
MCP_SERVER_URL=http://localhost:8000
```

### 2. Flutter Environment Variables

Create a `.env` file in your Flutter project root:

```bash
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.com
```

## Flutter Dependencies

Add these dependencies to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_dotenv: ^5.1.0
  livekit_client: ^1.5.0
  dart_jsonwebtoken: ^2.8.0
```

Run:
```bash
flutter pub get
```

## Running the Setup

### 1. Start the Python Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python worker.py
```

### 2. Test the Connection

```bash
# Test the Python server setup
python test_flutter_connection.py
```

### 3. Run the Flutter App

```bash
# Run the Flutter app
flutter run
```

## How It Works

### Connection Flow

1. **Flutter Client**:
   - Generates JWT token using API key/secret
   - Connects to LiveKit room
   - Publishes audio track
   - Sends/receives data messages

2. **Python Server**:
   - Listens for participant connections
   - Handles audio streams
   - Processes voice with STT/LLM/TTS
   - Sends responses back to client

### Key Components

#### Python Server (`worker.py`)
- **Event Handlers**: Properly handle async callbacks
- **Participant Management**: Track connected clients
- **Data Communication**: Send/receive messages with Flutter
- **Voice Processing**: STT → LLM → TTS pipeline

#### Flutter Client (`flutter_livekit_service.dart`)
- **Token Generation**: Secure JWT tokens
- **Room Connection**: Connect to LiveKit room
- **Audio Publishing**: Share microphone audio
- **Data Communication**: Send/receive messages

## Testing the Connection

### 1. Check Python Server Logs

Look for these log messages:
```
Room 'voice-assistant-room' is ready to accept connections
Flutter client connected: flutter-user-1234567890
Participant SID: PA_xxxxxxxx
Sent welcome message to flutter-user-1234567890
```

### 2. Check Flutter App

The app should show:
- ✅ Connected status
- 🤖 Welcome message from server
- 📱 Audio track published

### 3. Test Communication

1. **Text Messages**: Type in the text field and send
2. **Voice Commands**: Use "Start Voice" and "Stop Voice" buttons
3. **Data Exchange**: Check console logs for data messages

## Troubleshooting

### Common Issues

#### 1. Connection Failed
```
Error: LIVEKIT_URL not configured
```
**Solution**: Check your `.env` file has the correct LiveKit URL

#### 2. Authentication Error
```
Error: LIVEKIT_API_KEY/SECRET not configured
```
**Solution**: Verify API key and secret in `.env` file

#### 3. Room Not Found
```
Error: Room does not exist
```
**Solution**: Make sure Python server is running and room name matches

#### 4. Audio Track Issues
```
Error: Audio track not published
```
**Solution**: Check microphone permissions in Flutter app

### Debug Steps

1. **Check Environment Variables**:
   ```bash
   python test_flutter_connection.py
   ```

2. **Verify Python Server**:
   ```bash
   python worker.py
   ```

3. **Test Token Generation**:
   ```bash
   # In Flutter, check console for token generation logs
   ```

4. **Check Network Connectivity**:
   - Ensure LiveKit server is accessible
   - Check firewall settings
   - Verify WebSocket connection

## Advanced Configuration

### Custom Room Names

Change the room name in both Flutter and Python:

**Flutter**:
```dart
final token = _liveKitService.generateToken(
  userId: 'user-123',
  userName: 'John Doe',
  roomName: 'my-custom-room', // Change this
);
```

**Python**: The server will automatically use the room name from the token.

### Custom Attributes

Send custom data with your Flutter connection:

```dart
await _liveKitService.connectWithMic(
  token: token,
  attributes: {
    'platform': 'flutter',
    'version': '1.0.0',
    'user_type': 'mobile',
    'custom_field': 'custom_value',
  },
);
```

### Error Handling

The enhanced code includes comprehensive error handling:

- Connection failures
- Audio track issues
- Data message errors
- Network timeouts

## Security Considerations

1. **JWT Tokens**: Never expose API secret in client code
2. **Token Expiration**: Set appropriate TTL for tokens
3. **Room Access**: Use room-specific permissions
4. **Data Validation**: Validate all incoming data

## Performance Tips

1. **Audio Quality**: Adjust audio capture options for your use case
2. **Connection Pooling**: Reuse connections when possible
3. **Error Recovery**: Implement automatic reconnection logic
4. **Resource Cleanup**: Always dispose of resources properly

## Next Steps

1. **Voice Integration**: Connect your voice processing pipeline
2. **UI Enhancement**: Add voice visualization and controls
3. **Multi-user Support**: Handle multiple participants
4. **Persistence**: Add conversation history and user preferences