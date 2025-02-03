import 'package:flutter/material.dart';
import 'tracking_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'YOLO Tracking',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: TrackingScreen(),
    );
  }
}
