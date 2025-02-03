import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:async';

class TrackingScreen extends StatefulWidget {
  @override
  _TrackingScreenState createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  TextEditingController _urlController = TextEditingController();
  WebSocketChannel? _channel;
  List<Uint8List> _frames = [];
  int _currentFrameIndex = 0;
  bool _isTrackingStarted = false;
  bool _isConnecting = false; // Bağlantı durumu
  bool _isConnected = false; // Bağlantı durumu kontrolü

  // Frame rate (FPS)
  int frameRate = 30; // 30 FPS

  // Timer for frame display at specific rate
  Timer? _frameTimer;

  void startTracking() {
    if (_isConnecting || _isConnected) {
      // Eğer bağlantı kuruluyorsa veya bağlantı halindeyse yeni bağlantı başlatma
      return;
    }

    final String wsUrl = "ws://192.168.1.103:8000/ws"; // WebSocket URL

    setState(() {
      _isConnecting = true;
    });

    try {
      // WebSocket bağlantısını başlat
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text("WebSocket bağlantısı başarılı!"),
      ));

      // YouTube URL'sini WebSocket üzerinden gönder
      _channel?.sink.add(_urlController.text);

      // WebSocket'ten gelen mesajları dinle
      _channel?.stream.listen(
            (message) {
          setState(() {
            if (message is String) {
              // Base64 string formatındaki veriyi Uint8List'e dönüştür
              _frames.add(base64Decode(message));
            } else if (message is List<int>) {
              // Uint8List formatında mesaj
              _frames.add(Uint8List.fromList(message));
            }
          });
        },
        onError: (error) {
          setState(() {
            _isConnecting = false;
          });
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("WebSocket hata: $error"),
          ));
        },
        onDone: () {
          setState(() {
            _isConnected = false;
            _isConnecting = false;
          });
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("WebSocket bağlantısı kapatıldı."),
          ));
        },
      );

      // Başlangıçta, tracking başlamadan önce video frame'lerini doğru hızda göstermek için Timer başlatıyoruz
      setState(() {
        _isTrackingStarted = true;
        _isConnected = true;
      });

      _frameTimer = Timer.periodic(Duration(milliseconds: 1000 ~/ frameRate), (timer) {
        setState(() {
          // Frame ilerlet
          if (_frames.isNotEmpty) {
            _currentFrameIndex = (_currentFrameIndex + 1) % _frames.length;
          }
        });
      });
    } catch (e) {
      setState(() {
        _isConnecting = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text("WebSocket bağlantısı başarısız: $e"),
      ));
    }
  }

  @override
  void dispose() {
    // WebSocket bağlantısını kapat
    _channel?.sink.close();
    _frameTimer?.cancel();  // Timer'ı durdur
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("YOLOv8 Tracking")),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _urlController,
              decoration: InputDecoration(labelText: "YouTube Video URL"),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: startTracking,
              child: _isConnecting
                  ? CircularProgressIndicator() // Bağlantı yapılıyor gösterimi
                  : Text(_isConnected ? "Bağlantı Başlatıldı" : "Tracking Başlat"),
            ),
            SizedBox(height: 20),
            _frames.isNotEmpty
                ? Image.memory(
              _frames[_currentFrameIndex],
              fit: BoxFit.contain, // Orijinal boyutta görüntüle
              width: double.infinity,
              height: 360.0,
            )
                : Text(_isTrackingStarted ? "Görüntü bekleniyor..." : "Tracking başlatılmadı."),
          ],
        ),
      ),
    );
  }
}
