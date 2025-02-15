import 'package:flutter/material.dart';

class OutputTrackingScreen extends StatelessWidget {
  const OutputTrackingScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Output Tracking',
          style: TextStyle(
            color: Colors.white,
          ),
        ),
        backgroundColor: Color.fromRGBO(18,143,143, 1),
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Arka plan resmi
          Opacity(
            opacity: 0.5,
            child: Image.asset(
              'assets/background.png',
              fit: BoxFit.cover,
            ),
          ),
          Center(
            child: Text(
              'Output Tracking Page',
              style: TextStyle(fontSize: 24, color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }
}
