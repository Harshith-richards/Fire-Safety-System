import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../utils/constants.dart';
import '../../widgets/background_wrapper.dart';
import '../auth/login_screen.dart';
import '../history/history_screen.dart';

class AdminDashboard extends StatefulWidget {
  final String userEmail;
  final String userName;
  const AdminDashboard({super.key, required this.userEmail, required this.userName});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  Map<String, dynamic> _status = {};
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _fetchStatus();
    _timer = Timer.periodic(const Duration(seconds: 2), (timer) => _fetchStatus());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _fetchStatus() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/status'));
      if (response.statusCode == 200) {
        if (mounted) setState(() => _status = jsonDecode(response.body));
      }
    } catch (e) {
      debugPrint('$e');
    }
  }

  Future<void> _resetAlarm() async {
    try {
      await http.post(Uri.parse('$baseUrl/reset_alarm'));
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Alarm Reset')));
    } catch (e) {
      // Error
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isDanger = _status['alert_status'] == true;
    return Scaffold(
      appBar: AppBar(title: const Text('Admin Panel'), actions: [
        IconButton(onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (c) => const LoginScreen())), icon: const Icon(Icons.logout))
      ]),
      body: BackgroundWrapper(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(30),
                decoration: BoxDecoration(
                  color: isDanger ? Colors.red : Colors.green,
                  shape: BoxShape.circle,
                  boxShadow: [BoxShadow(color: (isDanger ? Colors.red : Colors.green).withValues(alpha: 0.5), blurRadius: 30)],
                ),
                child: Icon(isDanger ? Icons.warning : Icons.check, size: 50, color: Colors.white),
              ),
              const SizedBox(height: 20),
              Text(isDanger ? 'SYSTEM ALERT' : 'SYSTEM NORMAL', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: _resetAlarm,
                icon: const Icon(Icons.notifications_off),
                label: const Text('RESET ALARM'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (c) => HistoryScreen(userEmail: widget.userEmail))),
                icon: const Icon(Icons.history),
                label: const Text('VIEW LOGS'),
                style: ElevatedButton.styleFrom(backgroundColor: kSecondaryColor),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
