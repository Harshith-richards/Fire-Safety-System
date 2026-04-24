import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../utils/constants.dart';
import '../../widgets/background_wrapper.dart';
import '../../widgets/fade_animation.dart';

class HistoryScreen extends StatefulWidget {
  final String userEmail;
  const HistoryScreen({super.key, required this.userEmail});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> _logs = [];
  bool _isLoading = true;
  String? _errorMessage;
  Timer? _timer;


  @override
  void initState() {
    super.initState();
    _fetchLogs();
    _timer = Timer.periodic(const Duration(seconds: 20), (timer) => _fetchLogs(silent: true));
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _fetchLogs({bool silent = false}) async {
    if (!mounted) return;
    
    if (!silent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      print('Fetching logs for: ${widget.userEmail} (Silent: $silent)');
      final response = await http.get(Uri.parse('$baseUrl/logs?email=${widget.userEmail}'))
          .timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        if (mounted) {
          setState(() {
            _logs = jsonDecode(response.body);
            _isLoading = false;
            _errorMessage = null; // Clear error on success even if silent
          });
        }
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching logs: $e');
      if (mounted) {
        // Only show error UI if it's not a silent refresh
        if (!silent) {
          setState(() {
            _errorMessage = 'Failed to load logs. Please check your internet connection.';
            _isLoading = false;
          });
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: $e'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        } else {
           // On silent failure, maybe just print to console, don't disrupt user
           // Optional: You could show a small toast or icon
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Incident History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchLogs,
          )
        ],
      ),
      body: BackgroundWrapper(
        child: RefreshIndicator(
          onRefresh: _fetchLogs,
          child: _isLoading
              ? const Center(child: CircularProgressIndicator(color: kAccentColor))
              : _errorMessage != null
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline, size: 80, color: Colors.redAccent),
                          const SizedBox(height: 16),
                          Text(
                            _errorMessage!,
                            style: const TextStyle(color: Colors.white70),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                            onPressed: _fetchLogs,
                            icon: const Icon(Icons.refresh),
                            label: const Text('Retry'),
                            style: ElevatedButton.styleFrom(backgroundColor: kAccentColor),
                          )
                        ],
                      ),
                    )
                  : _logs.isEmpty
                      ? ListView( // Use ListView even for empty state to allow pull-to-refresh
                          children: [
                             SizedBox(height: MediaQuery.of(context).size.height * 0.3),
                             const Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.history, size: 80, color: Colors.white24),
                                    SizedBox(height: 16),
                                    Text('No incidents recorded yet', style: TextStyle(color: Colors.white54)),
                                  ],
                                ),
                             ),
                          ],
                        )
                      : ListView.builder(
                          physics: const AlwaysScrollableScrollPhysics(),
                          padding: const EdgeInsets.all(16),
                          itemCount: _logs.length,
                          itemBuilder: (context, index) {
                            final log = _logs[index];
                  final bool isDanger = log['status'] == 'DANGER';
                  final bool hasImage = log['image_url'] != null && log['image_url'].toString().isNotEmpty;
                  final bool hasPrediction = log['fire_class'] != null;
                  
                  return FadeInUp(
                    delay: Duration(milliseconds: index * 50),
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: kSecondaryColor,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: isDanger ? kAccentColor.withValues(alpha: 0.3) : Colors.white10,
                          width: isDanger ? 2 : 1,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Header
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: (isDanger ? kAccentColor : Colors.green).withValues(alpha: 0.1),
                                    shape: BoxShape.circle,
                                  ),
                                  child: Icon(
                                    isDanger ? Icons.warning_amber_rounded : Icons.check_circle_outline,
                                    color: isDanger ? kAccentColor : Colors.green,
                                    size: 24,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        log['status'] ?? 'UNKNOWN',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 18,
                                          color: isDanger ? kAccentColor : Colors.green,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        _formatTimestamp(log['timestamp']),
                                        style: const TextStyle(color: Colors.white54, fontSize: 12),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          
                          // Image if available
                          if (hasImage)
                            GestureDetector(
                              onTap: () {
                                // Show full screen image
                                showDialog(
                                  context: context,
                                  builder: (context) => Dialog(
                                    backgroundColor: Colors.transparent,
                                    child: Column(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        ClipRRect(
                                          borderRadius: BorderRadius.circular(20),
                                          child: Image.network(
                                            '$baseUrl${log['image_url']}',
                                            fit: BoxFit.contain,
                                            errorBuilder: (c, e, s) => Container(
                                              height: 200,
                                              color: Colors.black26,
                                              child: const Center(
                                                child: Icon(Icons.broken_image, size: 50, color: Colors.white24),
                                              ),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(height: 16),
                                        ElevatedButton.icon(
                                          onPressed: () => Navigator.pop(context),
                                          icon: const Icon(Icons.close),
                                          label: const Text('Close'),
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: kAccentColor,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                );
                              },
                              child: Container(
                                margin: const EdgeInsets.symmetric(horizontal: 16),
                                height: 200,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: Colors.white10),
                                ),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: Stack(
                                    fit: StackFit.expand,
                                    children: [
                                      Image.network(
                                        '$baseUrl${log['image_url']}',
                                        fit: BoxFit.cover,
                                        errorBuilder: (c, e, s) => Container(
                                          color: Colors.black26,
                                          child: const Center(
                                            child: Icon(Icons.broken_image, size: 50, color: Colors.white24),
                                          ),
                                        ),
                                      ),
                                      Positioned(
                                        top: 8,
                                        right: 8,
                                        child: Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                          decoration: BoxDecoration(
                                            color: Colors.black54,
                                            borderRadius: BorderRadius.circular(20),
                                          ),
                                          child: const Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              Icon(Icons.zoom_in, size: 16, color: Colors.white),
                                              SizedBox(width: 4),
                                              Text('Tap to enlarge', style: TextStyle(fontSize: 12)),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          
                          if (hasImage) const SizedBox(height: 16),
                          
                          // Sensor Data
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Row(
                              children: [
                                Expanded(
                                  child: _buildInfoChip(
                                    Icons.thermostat,
                                    'Temp',
                                    '${log['temperature'] ?? 'N/A'} °C',
                                    Colors.orange,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: _buildInfoChip(
                                    Icons.water_drop,
                                    'Humidity',
                                    '${log['humidity'] ?? 'N/A'} %',
                                    Colors.cyan,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          
                          const SizedBox(height: 12),
                          
                          // Prediction Results if available
                          if (hasPrediction)
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              child: Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: kAccentColor.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: kAccentColor.withValues(alpha: 0.3)),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        const Icon(Icons.local_fire_department, color: kAccentColor, size: 20),
                                        const SizedBox(width: 8),
                                        Text(
                                          'Fire Class: ${log['fire_class']}',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                            color: kAccentColor,
                                          ),
                                        ),
                                        const Spacer(),
                                        if (log['confidence'] != null)
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                            decoration: BoxDecoration(
                                              color: kAccentColor,
                                              borderRadius: BorderRadius.circular(12),
                                            ),
                                            child: Text(
                                              '${log['confidence']}%',
                                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                                            ),
                                          ),
                                      ],
                                    ),
                                    if (log['recommendation'] != null) ...[
                                      const SizedBox(height: 8),
                                      Text(
                                        log['recommendation'],
                                        style: const TextStyle(color: Colors.white70, fontSize: 13),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ),
                          
                          const SizedBox(height: 16),
                        ],
                      ),
                    ),
                  );
                },
              ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: TextStyle(color: color, fontSize: 10)),
                Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(dynamic timestamp) {
    try {
      if (timestamp == null) return 'Unknown time';
      DateTime dt = DateTime.parse(timestamp.toString());
      return '${dt.day}/${dt.month}/${dt.year} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return timestamp.toString();
    }
  }
}
