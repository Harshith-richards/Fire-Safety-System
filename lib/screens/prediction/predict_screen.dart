import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:http_parser/http_parser.dart';
import '../../utils/constants.dart';
import '../../widgets/background_wrapper.dart';
import '../../widgets/fade_animation.dart';

class PredictFireClassScreen extends StatefulWidget {
  final String userEmail;
  final String userName;
  const PredictFireClassScreen({super.key, required this.userEmail, required this.userName});

  @override
  State<PredictFireClassScreen> createState() => _PredictFireClassScreenState();
}

class _PredictFireClassScreenState extends State<PredictFireClassScreen> {
  XFile? _selectedImage;
  Uint8List? _imageBytes;
  bool _isLoading = false;
  Map<String, dynamic>? _predictionResult;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    final XFile? image = await _picker.pickImage(source: source);
    if (image != null) {
      final bytes = await image.readAsBytes();
      setState(() {
        _selectedImage = image;
        _imageBytes = bytes;
        _predictionResult = null;
      });
    }
  }

  Future<void> _predictFireClass() async {
    if (_selectedImage == null) return;
    setState(() => _isLoading = true);

    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/predict'));
      if (_imageBytes != null) {
        request.files.add(http.MultipartFile.fromBytes('image', _imageBytes!, filename: 'upload.jpg', contentType: MediaType('image', 'jpeg')));
      } else {
        request.files.add(await http.MultipartFile.fromPath('image', _selectedImage!.path, contentType: MediaType('image', 'jpeg')));
      }
      request.fields['user_email'] = widget.userEmail;
      request.fields['user_name'] = widget.userName;

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        setState(() {
          _predictionResult = jsonDecode(response.body);
        });
      } else {
        throw Exception('Prediction failed');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Fire Analysis')),
      body: BackgroundWrapper(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              Container(
                height: 300,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: kSecondaryColor,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.white10),
                ),
                child: _imageBytes != null
                    ? ClipRRect(borderRadius: BorderRadius.circular(20), child: Image.memory(_imageBytes!, fit: BoxFit.cover))
                    : Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: const [
                          Icon(Icons.cloud_upload_outlined, size: 60, color: Colors.white54),
                          SizedBox(height: 10),
                          Text('Upload an image to analyze', style: TextStyle(color: Colors.white54)),
                        ],
                      ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Camera'),
                      style: ElevatedButton.styleFrom(backgroundColor: kSecondaryColor),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _pickImage(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library),
                      label: const Text('Gallery'),
                      style: ElevatedButton.styleFrom(backgroundColor: kSecondaryColor),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _predictFireClass,
                  child: _isLoading 
                      ? Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
                            SizedBox(width: 10),
                            Text('Analyzing...'),
                          ],
                        )
                      : const Text('ANALYZE FIRE'),
                ),
              ),
              if (_predictionResult != null) ...[
                const SizedBox(height: 20),
                FadeInUp(
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [const Color(0xFFE53935).withValues(alpha: 0.2), const Color(0xFFE35D5B).withValues(alpha: 0.2)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: kAccentColor),
                    ),
                    child: Column(
                      children: [
                        const Icon(Icons.local_fire_department, size: 50, color: kAccentColor),
                        const SizedBox(height: 10),
                        const Text('Fire Class Detected', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        const SizedBox(height: 10),
                        Text(
                          _predictionResult!['predicted_class'] ?? 'Unknown',
                          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: kAccentColor),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          'Confidence: ${_predictionResult!['predicted_confidence']?.toStringAsFixed(1) ?? '0'}%',
                          style: const TextStyle(fontSize: 18, color: Colors.white70),
                        ),
                        const Divider(color: Colors.white10, height: 30),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.05),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: const [
                                  Icon(Icons.info_outline, color: Colors.white70, size: 20),
                                  SizedBox(width: 8),
                                  Text('Recommendation', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _predictionResult!['recommendation'] ?? 'No recommendation available',
                                style: const TextStyle(color: Colors.white70, fontSize: 13),
                              ),
                            ],
                          ),
                        ),
                        if (_predictionResult!['email_sent'] == true) ...[
                          const SizedBox(height: 15),
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: Colors.green.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: Colors.green),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: const [
                                Icon(Icons.check_circle, color: Colors.green, size: 18),
                                SizedBox(width: 8),
                                Text('Alert emails sent!', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ]
            ],
          ),
        ),
      ),
    );
  }
}
