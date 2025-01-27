import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:playfit/authentification/login_page.dart';
import 'package:playfit/authentification/registration_page.dart';
import 'package:playfit/home_page.dart';
import 'package:playfit/profile_page.dart';
import 'package:playfit/camera_page.dart';

void main() async {
  await dotenv.load(fileName: ".env");

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const LoginPage(),
      initialRoute: '/login',
      routes: {
        '/register': (context) =>
            const CreateAccountPage(), // Route to registration page
        '/login': (context) => const LoginPage(), // Route to login page
        '/home': (context) => const HomePage(), // Route to home page
        '/profile': (context) => const ProfilePage(), // Route to profile page
        '/camera': (context) => CameraView(), // Route to camera page
      },
    );
  }
}
