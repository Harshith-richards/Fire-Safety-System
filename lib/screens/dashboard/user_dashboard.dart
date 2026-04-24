import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:fl_chart/fl_chart.dart';
import 'package:geolocator/geolocator.dart';
import '../../utils/constants.dart';
import '../../widgets/background_wrapper.dart';
import '../../widgets/glass_box.dart';
import '../../widgets/fade_animation.dart';
import '../prediction/predict_screen.dart';

class UserDashboard extends StatefulWidget {
  final String userEmail;
  final String userName;
  const UserDashboard({super.key, required this.userEmail, required this.userName});

  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> {
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
        if (mounted) {
          setState(() {
            _status = jsonDecode(response.body);
          });
        }
      }
    } catch (e) {
      debugPrint('Error fetching status: $e');
    }
  }

  Future<void> _sendSosAlert() async {
    try {
      // Fetch current location
      String locationString = 'Lat: 0.0, Long: 0.0';
      try {
        Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
        locationString = 'Lat: ${position.latitude}, Long: ${position.longitude}';
        
        // Add Google Maps link
        locationString += '\nGoogle Maps: https://www.google.com/maps/search/?api=1&query=${position.latitude},${position.longitude}';
      } catch (e) {
        print('Error getting location for SOS: $e');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/sos'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': widget.userEmail,
          'location': locationString,
        }),
      );

      if (response.statusCode == 200) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('SOS Alert Sent! Help is on the way!'), backgroundColor: kAccentColor),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error sending SOS: $e'), backgroundColor: kAccentColor),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isDanger = _status['alert_status'] == true;
    final double temp = _status['temperature'] ?? 0.0;
    final double gas = _status['gas_level'] ?? 0.0;
    final String gasStatus = gas <= 50 ? 'Normal' : 'High';

    return BackgroundWrapper(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Welcome back,', style: TextStyle(color: Colors.white70, fontSize: 16)),
                    Text(widget.userName, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  ],
                ),
                CircleAvatar(
                  radius: 25,
                  backgroundColor: kSecondaryColor,
                  child: Text(widget.userName.isNotEmpty ? widget.userName[0] : 'U', style: const TextStyle(color: Colors.white)),
                ),
              ],
            ),
            const SizedBox(height: 30),
            // Status Card
            FadeInDown(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isDanger ? [const Color(0xFFE53935), const Color(0xFFE35D5B)] : [const Color(0xFF43A047), const Color(0xFF66BB6A)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: (isDanger ? Colors.red : Colors.green).withOpacity(0.4), blurRadius: 20, offset: const Offset(0, 10)),
                  ],
                ),
                child: Column(
                  children: [
                    Icon(isDanger ? Icons.warning_amber_rounded : Icons.check_circle_outline, size: 60, color: Colors.white),
                    const SizedBox(height: 10),
                    Text(
                      isDanger ? 'DANGER DETECTED' : 'SYSTEM SAFE',
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 1.2),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      isDanger ? 'Immediate action required!' : 'All sensors are normal',
                      style: const TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Sensors Grid
            SizedBox(
              height: 320, // Increased height
              child: GridView.count(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 0.9, // Adjusted aspect ratio
                physics: const NeverScrollableScrollPhysics(),
                children: [
                  FadeInLeft(child: _buildSensorCard('Temperature', '$temp °C', Icons.thermostat, Colors.orange)),
                  FadeInRight(child: _buildSensorCard('Humidity', '${_status['humidity'] ?? 50.0} %', Icons.water_drop, Colors.cyan)),
                  FadeInLeft(delay: const Duration(milliseconds: 200), child: _buildSensorCard('Gas Level', gasStatus, Icons.cloud, Colors.blue)),
                  FadeInRight(delay: const Duration(milliseconds: 200), child: _buildSensorCard('Device', '${_status['device_id'] ?? 'N/A'}', Icons.router, Colors.purple)),
                ],
              ),
            ),
            const SizedBox(height: 20),
            // Temperature Chart
            FadeInUp(
              child: GlassBox(
                height: 200,
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Temperature Trend', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white70)),
                    const SizedBox(height: 10),
                    Expanded(
                      child: LineChart(
                        LineChartData(
                          gridData: const FlGridData(show: false),
                          titlesData: const FlTitlesData(show: false),
                          borderData: FlBorderData(show: false),
                          lineBarsData: [
                            LineChartBarData(
                              spots: [
                                const FlSpot(0, 20),
                                const FlSpot(1, 25),
                                const FlSpot(2, 22),
                                const FlSpot(3, 30),
                                const FlSpot(4, 28),
                                FlSpot(5, temp),
                              ],
                              isCurved: true,
                              color: kAccentColor,
                              barWidth: 3,
                              isStrokeCapRound: true,
                              dotData: const FlDotData(show: false),
                              belowBarData: BarAreaData(
                                show: true,
                                color: kAccentColor.withOpacity(0.2),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: FadeInLeft(
                    child: GestureDetector(
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => PredictFireClassScreen(userEmail: widget.userEmail, userName: widget.userName))),
                      child: _buildActionCard('Predict Fire', Icons.camera_alt, Colors.purple),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: FadeInRight(
                    child: GestureDetector(
                      onTap: _sendSosAlert,
                      child: _buildActionCard('SOS Alert', Icons.sos, kAccentColor),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    ));
  }

  Widget _buildSensorCard(String title, String value, IconData icon, Color color) {
    return GlassBox(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: color.withOpacity(0.2), shape: BoxShape.circle),
            child: Icon(icon, color: color),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                FittedBox(
                  fit: BoxFit.scaleDown,
                  child: Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                ),
                Text(title, style: const TextStyle(color: Colors.white70, fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard(String title, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: kSecondaryColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 40, color: color),
          const SizedBox(height: 10),
          Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
