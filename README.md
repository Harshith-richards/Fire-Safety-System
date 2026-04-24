# 🔥 IoT & AI Fire Safety System

Welcome to the Fire Safety System Project! This comprehensive platform integrates IoT sensors (Temperature, Humidity, Gas) with robust AI (YOLO Image Recognition) to detect, classify, and automatically alert users of fire incidents in real-time.

This repository serves as the central hub for the Flutter App source, Python Machine Learning Backend, and the Arduino IoT firmware.

---

## 📦 Quick Setup & Installation

The project workspace is optimized for version control (meaning cached builds and virtual environments are excluded). After cloning or downloading this repository, you must recreate the dependencies on your machine. 

Here are the commands you need to spin everything up:

### 1. Python Backend & AI Setup
Our backend runs on Flask, uses MongoDB for user/logs storage, and incorporates the YOLOv8 model (`best.pt`) for smart fire classification.

```powershell
# 1. Open a terminal in the root project folder
cd "d:\project\final b9"

# 2. Create a fresh Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
venv\Scripts\activate

# 4. Install all backend dependencies
pip install -r requirements.txt

# 5. Start the backend server
python run.py
```
*(Note: Ensure MongoDB Community Server is installed and running background service on default port `27017`)*

### 2. Flutter Mobile Application Setup
Our frontend is a modern mobile application providing users a sleek dashboard to monitor live IoT sensors and alert histories.

```powershell
# 1. Navigate to the project root in a new terminal
cd "d:\project\final b9"

# 2. Clean old cache (if any)
flutter clean

# 3. Download and install frontend packages
flutter pub get

# 4. Update your backend IP!
# Open lib/utils/constants.dart and update the baseUrl with your local IP address.

# 5. Run the application
flutter run
```

---

## 📚 Detailed Documentation

This project contains several specialized guides tailored to different components of the system. For an in-depth dive into a specific feature, please follow these reference files:

*   📖 **[Submission & Architecture Overview](README_SUBMISSION.md)** - Comprehensive breakdown of features, project flows, and grading deliverables.
*   🚀 **[Start Servers Guide](START_SERVERS.md)** - Step-by-step commands on firing up the servers alongside troubleshooting.
*   🔌 **[ESP32 IoT Hardware Setup](ESP32_SETUP_GUIDE.md)** - Pinout diagrams, Arduino IDE setup, DHT11/MQ2 sensor configurations.
*   📱 **[APK Installation & Build Guide](APK_INSTALLATION_GUIDE.md)** - Steps to compile your final Flutter app into an Android App.
*   🌍 **[Global Access Setup](GLOBAL_ACCESS_SETUP.md)** - Guide on securely tunneling your local API over the internet (e.g. Cloudflare).
*   🧪 **[System Testing](TESTING_GUIDE.md)** - Methodology for tricking the sensors efficiently to test the fire detection algorithms.
*   📄 **[Test Reports](TEST_REPORT.md)** - Empirical results evaluated by the AI model during previous trials.
*   🚧 **[Future Enhancements](ENHANCEMENTS.md)** - Our roadmap detailing how this system can scale.

---

## ⚙️ How It Works (At A Glance)

1. **IoT Detection**: The standalone ESP32-CAM continuously monitors the environment and pushes live DHT11 (Temperature/Humidity) and MQ2 (Smoke/Gas) readings to the Flask backend.
2. **AI Classification**: Upon breaching critical environmental thresholds, the camera captures an image and invokes the YOLO model to categorize the flame (Class A, B, C, D, or K).
3. **Cloud Action**: The server triggers push pipelines, sending emergency warnings coupled with Extinguisher Recommendations to the user via Email.
4. **User Dashboard**: Through authentication, users track live statuses directly through the intuitive Flutter dashboard and view all critical logs securely.

---
**Developed for: 7th Semester Final Year Project**
