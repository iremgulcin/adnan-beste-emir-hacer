import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';

class TrackingService {
  WebSocketChannel? _channel;
  Function(Uint8List)? onFrameReceived;

  // Model tipleri ve WebSocket adresleri
  final Map<String, String> modelEndpoints = {
    'Detection': "ws://192.168.1.103:8000/detection_ws",
    'ByteTrack': "ws://192.168.1.103:8000/byte_track_ws",
  };

  void connect(String modelType, String videoUrl) {
    final normalizedModelType = modelType.trim();
    final String? wsUrl = modelEndpoints[normalizedModelType];

    if (wsUrl == null) {
      print("Geçersiz model tipi seçildi: $modelType");
      return;
    }

    // WebSocket bağlantısını aç
    _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
    print("WebSocket bağlantısı açıldı: $wsUrl");

    _channel?.stream.listen(
          (message) {
        if (message is String) {
          final Uint8List frameData = base64Decode(message);
          onFrameReceived?.call(frameData);
        }
      },
      onDone: () {
        print("WebSocket bağlantısı kapandı.");
      },
      onError: (error) {
        print("WebSocket hatası: $error");
      },
    );

    // Video URL'sini WebSocket üzerinden gönder
    _channel?.sink.add(jsonEncode({"video_url": videoUrl}));
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}
