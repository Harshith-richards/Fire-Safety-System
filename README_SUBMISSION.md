# Fire Safety IoT & AI Project - Submission CD

This directory contains the complete source code and documentation for the Fire Safety Project. This system integrates IoT sensors (Temperature, Humidity, Gas) with AI (YOLO Image Recognition) to detect and classify fire incidents in real-time.

## Project Contents
1. **Source Code**: 
   - `lib/`: Flutter Mobile Application source.
   - `app/` & `run.py`: Modular Flask Python Backend.
   - `server_backup.py`: Alternative single-file Flask Backend.
   - `iot_firmware/`: ESP32-CAM Source Code (Arduino).
2. **Project Report**: Soft copy of the Final Report (if available).
3. **Presentations**: Synopsis and Final PPT.
4. **Execution Video**: Step-by-step video demonstration.
5. **Software Requirements**: Detailed in `SPECIAL_SOFTWARE.txt`.

---

## 1. System Requirements

### Hardware
- **Laptop/PC**: Windows 10/11, 8GB RAM minimum.
- **Microcontroller**: ESP32-CAM (AI Thinker module).
- **Sensors**: 
  - **DHT11**: Temperature and Humidity sensing.
  - **MQ2**: Smoke/Gas detection.
- **Mobile Device**: Android Phone (for APK installation) or Chrome Browser (for web testing).

### Software
- **Python 3.12+**
- **Flutter SDK** (for app development/modification)
- **MongoDB Community Server** (Database)
- **Arduino IDE** (for ESP32 firmware upload)

---

## 2. Installation & Execution Steps

### Step 1: Database Setup
1. Install **MongoDB Community Server** and **MongoDB Compass**.
2. Ensure the MongoDB service is running on the default port `27017`.
3. The backend will automatically create the `fire_safety_db` database upon the first successful connection.

### Step 2: Backend (Python) Setup
The project provides two ways to run the backend:
- **Recommended (Modular)**: Run `python run.py`.
- **Alternative (Single-file)**: Run `python server_backup.py`.

**Execution Steps:**
1. Open a terminal in the project root folder.
2. Create and Activate Virtual Environment:
   ```bash
   python -m venv venv
   venv\Scripts\Activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Email Credentials (CRITICAL)**:
   - **For Modular Backend**: Open `app/config.py` and update `SENDER_EMAIL` and `SENDER_PASSWORD`.
   - **For Single-file Backend**: Open `server_backup.py` and search for `send_email_notification` to update credentials.
   - *Note: Use a Gmail "App Password", not your regular password.*
5. Run the server:
   ```bash
   python run.py
   ```
6. **Note the IP address** printed in the console (e.g., `192.168.1.5`).

### Step 3: Mobile App (Flutter) Setup
1. Open `lib/utils/constants.dart`.
2. Update the `baseUrl` variable with your Backend IP address:
   ```dart
   const String baseUrl = 'http://192.168.1.5:5000';
   ```
3. Run the application:
   - **For Web**: `flutter run -d chrome`
   - **For Android**: `flutter run`
   - **Build APK**: `flutter build apk --release` (Output: `build/app/outputs/flutter-apk/app-release.apk`)

### Step 4: IoT Firmware Setup
1. Open `iot_firmware/esp32_dht11/esp32_dht11.ino` in Arduino IDE.
2. Install required libraries: `DHT sensor library`, `WiFi`.
3. Select Board: **"AI Thinker ESP32-CAM"**.
4. Update **Wi-Fi SSID**, **Password**, and the **serverHost** (PC IP address).
5. Upload the code to the ESP32 module.

---

## 3. Project Working (Step-by-Step)

1. **User Authentication**: Register/Login via the Flutter app. Data is verified against MongoDB.
2. **Environment Monitoring**: 
   - ESP32-CAM reads temperature from DHT11 and smoke levels from MQ2.
   - Data is transmitted to the Flask server every few seconds.
3. **Fire Detection & AI Analysis**:
   - If thresholds are exceeded (High temp + Smoke), a "DANGER" status is triggered.
   - The system captures an image and sends it to the server.
   - The **YOLO AI Model (`best.pt`)** classifies the fire into types (Class A, B, C, D, or K).
4. **Alert System**:
   - The server sends automated **Email Notifications** to the user and emergency responders.
   - Recommended fire extinguisher types are provided based on the AI classification.
5. **Admin Control**:
   - Use the Admin login to monitor historical logs and **Reset the Alarm** once the emergency is handled.

---

## 4. Troubleshooting
- **Connection Failed**: Ensure both the PC and Mobile/ESP32 are on the **same Wi-Fi network**.
- **Email Not Sending**: Ensure "Less Secure App Access" is handled via **App Passwords** in your Google account.
- **Database Error**: Check if MongoDB service is running in Windows Services (`services.msc`).
- **Camera Error**: Ensure the ESP32-CAM has a stable 5V power supply.

---

**Developed for: 7th Semester Project Submission**
**Team: Fire Safety AI Solutions**
