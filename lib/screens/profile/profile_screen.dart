import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../../utils/constants.dart';
import '../../widgets/background_wrapper.dart';
import '../../widgets/glass_box.dart';
import '../../widgets/fade_animation.dart';
import '../auth/login_screen.dart';

class ProfileScreen extends StatefulWidget {
  final String userEmail;
  final String userName;
  const ProfileScreen({super.key, required this.userEmail, required this.userName});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic> _userData = {};
  bool _isLoading = true;
  bool _isUpdatingLocation = false;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/profile?email=${widget.userEmail}'),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          setState(() {
            _userData = jsonDecode(response.body);
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() => _isLoading = false);
        }
      }
    } catch (e) {
      debugPrint('Error fetching profile: $e');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _updateLocation() async {
    setState(() => _isUpdatingLocation = true);
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw 'Location permissions are denied';
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        throw 'Location permissions are permanently denied';
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      String address = _userData['address'] ?? '';
      try {
        List<Placemark> placemarks = await placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        );
        
        if (placemarks.isNotEmpty) {
          Placemark place = placemarks[0];
          address = '${place.street}, ${place.locality}, ${place.postalCode}, ${place.country}';
        }
      } catch (e) {
        print('Geocoding error: $e');
      }

      // Update backend
      final response = await http.post(
        Uri.parse('$baseUrl/update_profile'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': widget.userEmail,
          'address': address,
          'latitude': position.latitude,
          'longitude': position.longitude,
        }),
      );

      if (response.statusCode == 200) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Location updated successfully!'), backgroundColor: Colors.green),
        );
        _fetchProfile(); // Refresh profile
      } else {
        throw Exception('Failed to update profile');
      }

    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error updating location: $e'), backgroundColor: kAccentColor),
      );
    } finally {
      if (mounted) setState(() => _isUpdatingLocation = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: BackgroundWrapper(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: kAccentColor))
            : SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    const SizedBox(height: 20),
                    Stack(
                      alignment: Alignment.bottomRight,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(shape: BoxShape.circle, color: kAccentColor),
                          child: CircleAvatar(
                            radius: 60,
                            backgroundColor: kSecondaryColor,
                            child: Text(
                              widget.userName.isNotEmpty ? widget.userName[0].toUpperCase() : 'U',
                              style: const TextStyle(fontSize: 40, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: const BoxDecoration(color: kAccentColor, shape: BoxShape.circle),
                          child: const Icon(Icons.edit, color: Colors.white, size: 20),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Text(
                      _userData['name'] ?? widget.userName,
                      style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      _userData['email'] ?? widget.userEmail,
                      style: const TextStyle(color: Colors.white70, fontSize: 16),
                    ),
                    const SizedBox(height: 40),
                    FadeInUp(
                      child: GlassBox(
                        child: Column(
                          children: [
                            _buildProfileItem(
                              Icons.phone,
                              'Phone',
                              _userData['phone']?.isNotEmpty == true ? _userData['phone'] : 'Not set',
                            ),
                            const Divider(color: Colors.white10),
                            _buildProfileItem(
                              Icons.location_on,
                              'Address',
                              _userData['address']?.isNotEmpty == true ? _userData['address'] : 'Not set',
                              trailing: IconButton(
                                onPressed: _isUpdatingLocation ? null : _updateLocation,
                                icon: _isUpdatingLocation 
                                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                                  : const Icon(Icons.my_location, color: kAccentColor),
                                tooltip: 'Update Location',
                              ),
                            ),
                            const Divider(color: Colors.white10),
                            _buildProfileItem(
                              Icons.security,
                              'Role',
                              (_userData['role'] ?? 'user').toUpperCase(),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    FadeInUp(
                      delay: const Duration(milliseconds: 200),
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.pushAndRemoveUntil(
                            context,
                            MaterialPageRoute(builder: (context) => const LoginScreen()),
                            (route) => false,
                          );
                        },
                        icon: const Icon(Icons.logout),
                        label: const Text('LOGOUT'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.redAccent,
                          minimumSize: const Size(double.infinity, 50),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildProfileItem(IconData icon, String title, String value, {Widget? trailing}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.1), shape: BoxShape.circle),
            child: Icon(icon, color: kAccentColor, size: 20),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white54, fontSize: 12)),
                Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
              ],
            ),
          ),
          if (trailing != null) trailing,
        ],
      ),
    );
  }
}
