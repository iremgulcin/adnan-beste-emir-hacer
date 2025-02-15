import 'package:flutter/material.dart';
import 'tracking_service.dart';

class TrackingScreen extends StatefulWidget {
  final String videoUrl;

  const TrackingScreen({Key? key, required this.videoUrl}) : super(key: key);

  @override
  _TrackingScreenState createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  String selectedModel = 'Detection'; // Varsayılan model
  late TrackingService trackingService;

  @override
  void initState() {
    super.initState();
    trackingService = TrackingService();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Takip Ekranı'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          DropdownButton<String>(
            value: selectedModel,
            items: const [
              DropdownMenuItem(value: 'Detection', child: Text('Detection')),
              DropdownMenuItem(value: 'ByteTrack', child: Text('ByteTrack')),
            ],
            onChanged: (value) {
              if (value != null) {
                setState(() {
                  selectedModel = value;
                });
              }
            },
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {
              trackingService.connect(selectedModel, widget.videoUrl);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('$selectedModel ile takip başlatıldı!')),
              );
            },
            child: const Text('Takip Başlat'),
          ),
        ],
      ),
    );
  }
}
