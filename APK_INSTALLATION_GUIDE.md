# 📱 Android APK Installation Guide

## ✅ APK Successfully Built!

**Source Folder**: `d:\final b9`
**Output Location**: `build\app\outputs\flutter-apk\app-release.apk`

---

## 📋 Installation Steps

### 1️⃣ **Transfer APK to Android Device**
- Connect your Android phone via USB.
- Copy `app-release.apk` to your phone's Downloads folder.
- OR email it to yourself and download on the phone.
- OR use a file-sharing service (Google Drive, WhatsApp, etc.).

### 2️⃣ **Enable Unknown Sources**
- Go to **Settings** → **Security**.
- Enable **Install from Unknown Sources** (or similar option).
- On newer Android: Settings → Apps → Special Access → Install Unknown Apps.

### 3️⃣ **Install the APK**
- Open **File Manager** on your phone.
- Navigate to the folder where you saved the APK.
- Tap on `app-release.apk`.
- Tap **Install**.
- Tap **Open** after installation.

---

## 🌐 Network Setup (IMPORTANT!)

### Before using the app, ensure:

1. **Server is Running**
   ```bash
   cd "d:\final b9"
   venv\Scripts\python.exe run.py
   ```

2. **Phone and PC on Same WiFi Network**
   - Both devices must be connected to the same WiFi.
   - The server will print its IP address (e.g., `192.168.1.5:5000`).

3. **Windows Firewall Settings**
   - Allow incoming connections on port 5000.
   - Run this command in PowerShell (as Administrator):
   ```powershell
   New-NetFirewallRule -DisplayName "Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```

---

## 🧪 Testing the App

1. **Open the app** on your Android device.
2. **Register** a new account or **Login**.
3. **Dashboard** should show real-time sensor data (ensure the backend is running).
4. **Test Fire Prediction**:
   - Tap "Predict Fire" button.
   - Upload/capture a fire image.
   - Tap "ANALYZE FIRE".
   - AI will classify the fire and provide recommendations.
   - Email notifications are sent to both the user and emergency responders.

---

## 🔧 Troubleshooting

### ❌ "Cannot connect to server"
- **Check**: Both devices are on the same WiFi.
- **Check**: Server is running and showing the correct IP.
- **Check**: Firewall allows port 5000.
- **Test**: Open `http://<YOUR_PC_IP>:5000/status` in your phone's browser.

### ❌ "Prediction taking too long"
- **Check**: Server logs for errors.
- **Check**: YOLO model (`best.pt`) is present in the project root.
- **Note**: The first prediction may take a few extra seconds to initialize the model.

### 🔄 **Updating the Server IP**
If your PC's IP address changes, you must update the `baseUrl` in `lib/utils/constants.dart`:
```dart
const String baseUrl = 'http://YOUR_NEW_IP:5000';
```
Then rebuild the APK: `flutter build apk --release`.

---

## 📝 Notes

- **MongoDB**: Ensure the MongoDB service is running before starting the server.
- **Email Config**: Update your Gmail App Password in `app/config.py`.
- **Features**: Real-time monitoring, AI classification, Email alerts, and SOS functionality are all active.

**Safe and Smart Fire Monitoring! 🔥🚨**
