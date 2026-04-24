# 🚀 Quick Start Guide - Running Servers

## Prerequisites
- MongoDB installed and running.
- Python virtual environment set up.
- Flutter SDK installed.

---

## 🎯 Execution Steps

### Step 1: Start Flask Backend (Terminal 1)
```powershell
cd "d:\final b9"
venv\Scripts\activate
python run.py
```
**Expected Output:**
- `Connected to MongoDB successfully.`
- `✅ YOLO model loaded successfully from best.pt`
- `Server running on http://<IP_ADDRESS>:5000`

✅ **Keep this terminal open!**

---

### Step 2: Configure & Run Flutter App (Terminal 2)

**1. Update the Server IP:**
- Open `lib/utils/constants.dart`.
- Update the `baseUrl` with the IP address shown in **Terminal 1**:
  ```dart
  const String baseUrl = 'http://192.168.1.5:5000';
  ```
- Save the file.

**2. Run the App:**
```powershell
cd "d:\final b9"
flutter run -d windows
# OR for Android
flutter run
```

---

## 📱 Building APK for Android
If you want to install it on a phone:
1. Update `baseUrl` in `lib/utils/constants.dart` with your PC's IP.
2. Run: `flutter build apk --release`.
3. Locate APK at: `build\app\outputs\flutter-apk\app-release.apk`.

---

## 🆘 Quick Troubleshooting
- **MongoDB Error**: Run `net start MongoDB` in an Administrator terminal.
- **Connection Failed**: Ensure phone and PC are on the **same Wi-Fi**.
- **Model Error**: Ensure `best.pt` is in the project root folder.

**Fire Safety System is now active! 🔥🚨**
