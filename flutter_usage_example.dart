import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'flutter_livekit_service.dart';

void main() async {
  await dotenv.load(fileName: ".env");
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LiveKit Voice Assistant',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: VoiceAssistantScreen(),
    );
  }
}

class VoiceAssistantScreen extends StatefulWidget {
  @override
  _VoiceAssistantScreenState createState() => _VoiceAssistantScreenState();
}

class _VoiceAssistantScreenState extends State<VoiceAssistantScreen> {
  final LiveKitService _liveKitService = LiveKitService();
  bool _isConnected = false;
  bool _isConnecting = false;
  String _statusMessage = 'Not connected';
  List<String> _messages = [];
  final TextEditingController _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _setupDataListener();
  }

  void _setupDataListener() {
    _liveKitService.dataStream.listen((data) {
      setState(() {
        if (data['type'] == 'welcome') {
          _messages.add('🤖 ${data['message']}');
        } else if (data['type'] == 'response') {
          _messages.add('🤖 ${data['text']}');
        } else if (data['type'] == 'command_response') {
          _messages.add('⚙️ Command ${data['command']}: ${data['status']}');
        }
      });
    });
  }

  Future<void> _connectToRoom() async {
    if (_isConnecting) return;

    setState(() {
      _isConnecting = true;
      _statusMessage = 'Connecting...';
    });

    try {
      // Generate token
      final token = _liveKitService.generateToken(
        userId: 'flutter-user-${DateTime.now().millisecondsSinceEpoch}',
        userName: 'Flutter User',
        roomName: 'voice-assistant-room',
      );

      // Connect to room
      await _liveKitService.connectWithMic(
        token: token,
        attributes: {
          'platform': 'flutter',
          'version': '1.0.0',
          'user_type': 'mobile',
        },
      );

      setState(() {
        _isConnected = true;
        _isConnecting = false;
        _statusMessage = 'Connected to voice assistant';
        _messages.add('✅ Connected to voice assistant');
      });

    } catch (e) {
      setState(() {
        _isConnecting = false;
        _statusMessage = 'Connection failed: $e';
        _messages.add('❌ Connection failed: $e');
      });
    }
  }

  Future<void> _disconnectFromRoom() async {
    try {
      await _liveKitService.disconnect();
      setState(() {
        _isConnected = false;
        _statusMessage = 'Disconnected';
        _messages.add('🔌 Disconnected from voice assistant');
      });
    } catch (e) {
      setState(() {
        _statusMessage = 'Disconnect error: $e';
        _messages.add('❌ Disconnect error: $e');
      });
    }
  }

  Future<void> _sendTextMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty || !_isConnected) return;

    try {
      await _liveKitService.sendTextMessage(text);
      setState(() {
        _messages.add('👤 You: $text');
        _textController.clear();
      });
    } catch (e) {
      setState(() {
        _messages.add('❌ Error sending message: $e');
      });
    }
  }

  Future<void> _startConversation() async {
    if (!_isConnected) return;

    try {
      await _liveKitService.startConversation();
      setState(() {
        _messages.add('🎤 Started voice conversation');
      });
    } catch (e) {
      setState(() {
        _messages.add('❌ Error starting conversation: $e');
      });
    }
  }

  Future<void> _stopConversation() async {
    if (!_isConnected) return;

    try {
      await _liveKitService.stopConversation();
      setState(() {
        _messages.add('🔇 Stopped voice conversation');
      });
    } catch (e) {
      setState(() {
        _messages.add('❌ Error stopping conversation: $e');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Voice Assistant'),
        backgroundColor: _isConnected ? Colors.green : Colors.red,
      ),
      body: Column(
        children: [
          // Status and connection controls
          Container(
            padding: EdgeInsets.all(16),
            color: Colors.grey[100],
            child: Column(
              children: [
                Text(
                  _statusMessage,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: _isConnected ? Colors.green : Colors.red,
                  ),
                ),
                SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(
                      onPressed: _isConnecting ? null : _connectToRoom,
                      child: Text(_isConnecting ? 'Connecting...' : 'Connect'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                    ElevatedButton(
                      onPressed: _isConnected ? _disconnectFromRoom : null,
                      child: Text('Disconnect'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
                if (_isConnected) ...[
                  SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton(
                        onPressed: _startConversation,
                        child: Text('Start Voice'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                        ),
                      ),
                      ElevatedButton(
                        onPressed: _stopConversation,
                        child: Text('Stop Voice'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),

          // Text input
          if (_isConnected)
            Container(
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      decoration: InputDecoration(
                        hintText: 'Type a message...',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _sendTextMessage(),
                    ),
                  ),
                  SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _sendTextMessage,
                    child: Text('Send'),
                  ),
                ],
              ),
            ),

          // Messages
          Expanded(
            child: Container(
              padding: EdgeInsets.all(16),
              child: ListView.builder(
                reverse: true,
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  final message = _messages[_messages.length - 1 - index];
                  return Container(
                    margin: EdgeInsets.only(bottom: 8),
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: message.startsWith('👤') 
                          ? Colors.blue[100] 
                          : Colors.grey[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(message),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _liveKitService.dispose();
    _textController.dispose();
    super.dispose();
  }
}