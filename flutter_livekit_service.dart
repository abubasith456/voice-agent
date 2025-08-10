import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:livekit_client/livekit_client.dart' as lk;
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';

class LiveKitService {
  lk.Room? _room;
  lk.LocalParticipant? _localParticipant;
  
  // Stream controllers for communication
  final StreamController<Map<String, dynamic>> _dataStreamController = 
      StreamController<Map<String, dynamic>>.broadcast();
  
  Stream<Map<String, dynamic>> get dataStream => _dataStreamController.stream;

  String generateToken({
    required String userId,
    required String userName,
    String roomName = 'voice-assistant-room',
    Duration ttl = const Duration(hours: 1),
  }) {
    final apiKey = dotenv.env['LIVEKIT_API_KEY'];
    final apiSecret = dotenv.env['LIVEKIT_API_SECRET'];
    
    if (apiKey == null || apiSecret == null || apiKey.isEmpty || apiSecret.isEmpty) {
      throw Exception('LIVEKIT_API_KEY/SECRET not configured');
    }

    final now = DateTime.now().toUtc();
    final exp = now.add(ttl);

    final claims = <String, dynamic>{
      'iss': apiKey,
      'sub': userId,
      'name': userName,
      'nbf': (now.millisecondsSinceEpoch / 1000).floor(),
      'exp': (exp.millisecondsSinceEpoch / 1000).floor(),
      'video': {
        'roomCreate': true,
        'roomJoin': true,
        'room': roomName,
        'canPublish': true,
        'canSubscribe': true,
      },
    };

    final jwt = JWT(claims);
    return jwt.sign(SecretKey(apiSecret), algorithm: JWTAlgorithm.HS256);
  }

  Future<lk.Room> connectWithMic({
    required String token,
    required Map<String, String> attributes,
  }) async {
    final url = dotenv.env['LIVEKIT_URL'];
    if (url == null || url.isEmpty) {
      throw Exception('LIVEKIT_URL not configured');
    }

    try {
      // Create room with enhanced options
      _room = lk.Room(
        roomOptions: const lk.RoomOptions(
          adaptiveStream: true,
          dynacast: true,
          stopLocalTrackOnUnpublish: true,
        ),
      );

      // Set up room event listeners
      _setupRoomEventListeners();

      // Connect to the room
      await _room!.connect(url, token);
      print('Successfully connected to LiveKit room: ${_room!.name}');

      // Get local participant
      _localParticipant = _room!.localParticipant;
      if (_localParticipant == null) {
        throw Exception('Local participant not available');
      }

      // Set participant attributes
      try {
        _localParticipant!.setAttributes(attributes);
        print('Set participant attributes: $attributes');
      } catch (e) {
        print('Warning: Could not set participant attributes: $e');
      }

      // Create and publish audio track
      await _setupAudioTrack();

      return _room!;
      
    } catch (e) {
      print('Error connecting to LiveKit: $e');
      rethrow;
    }
  }

  void _setupRoomEventListeners() {
    if (_room == null) return;

    // Participant connected
    _room!.on(lk.RoomEvent.participantConnected, (participant) {
      print('Participant connected: ${participant.identity}');
      print('Participant SID: ${participant.sid}');
      print('Participant metadata: ${participant.metadata}');
    });

    // Participant disconnected
    _room!.on(lk.RoomEvent.participantDisconnected, (participant) {
      print('Participant disconnected: ${participant.identity}');
    });

    // Data received
    _room!.on(lk.RoomEvent.dataReceived, (data) {
      print('Data received: ${data.data}');
      _handleDataReceived(data);
    });

    // Track published
    _room!.on(lk.RoomEvent.trackPublished, (track, participant) {
      print('Track published by ${participant.identity}: ${track.sid}');
    });

    // Track subscribed
    _room!.on(lk.RoomEvent.trackSubscribed, (track, participant) {
      print('Track subscribed from ${participant.identity}: ${track.sid}');
    });

    // Connection state changes
    _room!.on(lk.RoomEvent.connectionStateChanged, (state) {
      print('Connection state changed: $state');
    });

    // Room state changes
    _room!.on(lk.RoomEvent.roomMetadataChanged, (metadata) {
      print('Room metadata changed: $metadata');
    });
  }

  Future<void> _setupAudioTrack() async {
    if (_localParticipant == null) return;

    try {
      // Create audio track with enhanced options
      final audioTrack = await lk.LocalAudioTrack.create(
        lk.AudioCaptureOptions(
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000,
          channelCount: 1,
        ),
      );

      // Publish the audio track
      await _localParticipant!.publishAudioTrack(audioTrack);
      print('Audio track published successfully');

      // Set up audio track event listeners
      audioTrack.on(lk.TrackEvent.muted, () {
        print('Audio track muted');
      });

      audioTrack.on(lk.TrackEvent.unmuted, () {
        print('Audio track unmuted');
      });

    } catch (e) {
      print('Error setting up audio track: $e');
      rethrow;
    }
  }

  void _handleDataReceived(lk.DataReceivedEvent data) {
    try {
      final dataString = data.data as String;
      final jsonData = jsonDecode(dataString) as Map<String, dynamic>;
      
      print('Parsed data: $jsonData');
      
      // Emit data to stream
      _dataStreamController.add(jsonData);
      
    } catch (e) {
      print('Error parsing received data: $e');
    }
  }

  // Send text message to the server
  Future<void> sendTextMessage(String text) async {
    if (_localParticipant == null) {
      throw Exception('Not connected to room');
    }

    try {
      final message = {
        'type': 'text',
        'text': text,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };

      await _localParticipant!.sendData(
        data: jsonEncode(message),
        topic: 'chat',
      );
      
      print('Text message sent: $text');
      
    } catch (e) {
      print('Error sending text message: $e');
      rethrow;
    }
  }

  // Send command to the server
  Future<void> sendCommand(String command) async {
    if (_localParticipant == null) {
      throw Exception('Not connected to room');
    }

    try {
      final message = {
        'type': 'command',
        'command': command,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };

      await _localParticipant!.sendData(
        data: jsonEncode(message),
        topic: 'system',
      );
      
      print('Command sent: $command');
      
    } catch (e) {
      print('Error sending command: $e');
      rethrow;
    }
  }

  // Start voice conversation
  Future<void> startConversation() async {
    await sendCommand('start_conversation');
  }

  // Stop voice conversation
  Future<void> stopConversation() async {
    await sendCommand('stop_conversation');
  }

  // Disconnect from the room
  Future<void> disconnect() async {
    try {
      if (_room != null) {
        await _room!.disconnect();
        print('Disconnected from LiveKit room');
      }
      
      _room = null;
      _localParticipant = null;
      
    } catch (e) {
      print('Error disconnecting: $e');
      rethrow;
    }
  }

  // Get room information
  Map<String, dynamic>? getRoomInfo() {
    if (_room == null) return null;
    
    return {
      'name': _room!.name,
      'sid': _room!.sid,
      'participantCount': _room!.participants.length,
      'connectionState': _room!.connectionState.toString(),
    };
  }

  // Get local participant information
  Map<String, dynamic>? getLocalParticipantInfo() {
    if (_localParticipant == null) return null;
    
    return {
      'identity': _localParticipant!.identity,
      'sid': _localParticipant!.sid,
      'metadata': _localParticipant!.metadata,
      'audioTracks': _localParticipant!.audioTracks.length,
    };
  }

  // Dispose resources
  void dispose() {
    _dataStreamController.close();
    disconnect();
  }
}