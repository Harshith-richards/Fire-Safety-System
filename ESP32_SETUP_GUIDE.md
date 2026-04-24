# 🔥 ESP32-CAM IoT Setup Guide - Fire Safety System

## 📋 Overview

This guide will help you set up the ESP32-CAM with DHT11 sensor to send real-time fire detection data to your cloud-based Flask backend.

---

## 🛠️ Hardware Requirements

- **ESP32-CAM** (AI-Thinker module)
- **DHT11** Temperature & Humidity Sensor
- **FTDI Programmer** (for uploading code)
- **Jumper Wires**
- **Power Supply** (5V)

---

## 📌 Wiring Diagram

### DHT11 to ESP32-CAM:
```
DHT11 Pin    →    ESP32-CAM Pin
─────────────────────────────────
VCC          →    5V
GND          →    GND
DATA         →    GPIO 13
```

### FTDI to ESP32-CAM (for programming):
```
FTDI Pin     →    ESP32-CAM Pin
─────────────────────────────────
5V           →    5V
GND          →    GND
TX           →    U0R (RX)
RX           →    U0T (TX)
GND          →    GPIO 0 (for upload mode)
```

> **Note:** Connect GPIO 0 to GND only when uploading code. Disconnect after upload!

---

## 💻 Arduino IDE Setup

### Step 1: Install ESP32 Board Support

1. Open **Arduino IDE**
2. Go to **File → Preferences**
3. Add this URL to "Additional Boards Manager URLs":
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "esp32" and install **ESP32 by Espressif Systems**

### Step 2: Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

- **DHT sensor library** by Adafruit
- **Adafruit Unified Sensor** (dependency for DHT)

### Step 3: Board Configuration

1. **Tools → Board** → Select **"AI Thinker ESP32-CAM"**
2. **Tools → Upload Speed** → **115200**
3. **Tools → Flash Frequency** → **80MHz**
4. **Tools → Partition Scheme** → **"Huge APP (3MB No OTA/1MB SPIFFS)"**
5. **Tools → Port** → Select your FTDI COM port

---

## 📝 Code Configuration

### Step 1: Open the Arduino Code

1. Navigate to `e:\antigravity\esp32_cam_iot\`
2. Open `esp32_cam_iot.ino` in Arduino IDE

### Step 2: Update WiFi Credentials

Find these lines and update with your WiFi details:

```cpp
const char* ssid       = "Hotspot";           // ← Your WiFi SSID
const char* password   = "12345678";          // ← Your WiFi Password
```

### Step 3: Verify Server URL

The server URL is already configured for your Cloudflare tunnel:

```cpp
const char* serverHost = "overcome-gates-andale-panels.trycloudflare.com";
```

> **Important:** If your Cloudflare tunnel URL changes, update this line!

### Step 4: Adjust Alert Thresholds (Optional)

```cpp
#define TEMP_ALERT_C     40.0   // Fire alert temperature (°C)
#define HUMIDITY_LOW_PCT  25.0  // Low humidity threshold (%)
```

---

## 📤 Upload Code to ESP32-CAM

### Step 1: Enter Upload Mode

1. Connect **GPIO 0** to **GND** on ESP32-CAM
2. Connect FTDI to computer
3. Press **RESET** button on ESP32-CAM

### Step 2: Upload

1. Click **Upload** button in Arduino IDE
2. Wait for "Connecting..." message
3. If stuck, press **RESET** button again
4. Wait for upload to complete (shows "Hard resetting via RTS pin...")

### Step 3: Run Mode

1. **Disconnect GPIO 0 from GND**
2. Press **RESET** button
3. Open **Serial Monitor** (Tools → Serial Monitor, 115200 baud)

---

## 🖥️ Serial Monitor Output

You should see:

```
╔════════════════════════════════════════╗
║  ESP32-CAM + DHT11 Fire Alert Node    ║
║  IoT Fire Safety System v2.0           ║
╚════════════════════════════════════════╝

✅ Camera initialized successfully
✅ DHT11 sensor initialized
Connecting to WiFi: Hotspot
........
✅ WiFi connected. ESP32 IP: 192.168.x.x

🚀 System ready! Monitoring environment...

🌡️  Temp: 25.0 °C | 💧 Humidity: 60.0 %
✅ OK: Environment normal.
─────────────────────────────────────────
```

---

## 🔥 Testing Fire Alert

### Method 1: Heat the DHT11 Sensor

1. Use a hair dryer or heat source
2. Heat the DHT11 sensor above 40°C
3. Wait for 3 consecutive high readings
4. ESP32 will:
   - Capture image
   - Send to server
   - Server runs fire prediction
   - Emails sent to user & emergency responders

### Method 2: Modify Threshold (for testing)

Temporarily change the threshold:

```cpp
#define TEMP_ALERT_C     30.0   // Lower threshold for testing
```

---

## 📊 Expected Behavior

### Normal Operation:
```
🌡️  Temp: 25.0 °C | 💧 Humidity: 60.0 %
✅ OK: Environment normal.
```

### Alert Triggered:
```
🌡️  Temp: 42.0 °C | 💧 Humidity: 20.0 %
🌡️  Temp: 43.0 °C | 💧 Humidity: 19.0 %
🌡️  Temp: 44.0 °C | 💧 Humidity: 18.0 %

🚨 ═══════════════════════════════════════
   ALERT: High temperature / low humidity!
   ═══════════════════════════════════════

📸 Image captured: 15234 bytes
📡 Connecting to overcome-gates-andale-panels.trycloudflare.com:443
✅ Connected to server
📤 Report sent, waiting for response...
HTTP/1.1 200 OK
{"status":"success","prediction":{"predicted_class":"Class_A",...}}
🔌 Connection closed
✅ Alert sent successfully!
```

---

## 🌐 Verify Data on Dashboard

1. Open your Flutter app (web or mobile)
2. Login to your account
3. Check the dashboard:
   - **Temperature** should show real ESP32 data
   - **Humidity** should update from DHT11
   - **Device** should show "esp32_cam_dht11"
   - **Last Updated** timestamp should be recent

---

## 🔧 Troubleshooting

### Issue: WiFi Connection Failed

**Solutions:**
- Check SSID and password are correct
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router
- Check if WiFi has MAC address filtering

### Issue: Camera Init Failed

**Solutions:**
- Check camera ribbon cable connection
- Ensure proper power supply (5V, at least 500mA)
- Try pressing RESET button
- Re-upload code

### Issue: DHT11 Read Failed

**Solutions:**
- Check wiring (VCC, GND, DATA to GPIO 13)
- Ensure DHT11 is not faulty (test with multimeter)
- Add 10kΩ pull-up resistor between DATA and VCC

### Issue: Connection to Server Failed

**Solutions:**
- Verify Cloudflare tunnel is running
- Check server URL in code matches tunnel URL
- Ensure Flask server is running
- Test tunnel URL in browser: `https://your-url.trycloudflare.com/status`

### Issue: SSL/HTTPS Errors

**Solutions:**
- Code uses `client.setInsecure()` to skip certificate validation
- This is normal for Cloudflare tunnels
- If issues persist, check WiFi allows HTTPS connections

### Issue: Image Upload Fails

**Solutions:**
- Reduce image quality: Change `config.jpeg_quality = 15` (higher number = lower quality)
- Use smaller frame size: Change to `FRAMESIZE_QVGA`
- Check network stability

---

## 📈 Performance Tips

### Reduce Power Consumption:
```cpp
// Add deep sleep between readings
esp_sleep_enable_timer_wakeup(60 * 1000000); // 60 seconds
esp_deep_sleep_start();
```

### Improve Image Quality:
```cpp
config.jpeg_quality = 10;  // Lower = better quality (but larger file)
config.frame_size = FRAMESIZE_SVGA;  // Higher resolution
```

### Faster Response:
```cpp
// Reduce consecutive readings needed for alert
if (highCount >= 2) { // Instead of 3
```

---

## 🔒 Security Recommendations

> **WARNING:** Your ESP32 sends data over the internet!

### Recommended Improvements:

1. **Add Device Authentication:**
```cpp
// Add authentication token
startPart += "--" + boundary + "\r\n";
startPart += "Content-Disposition: form-data; name=\"auth_token\"\r\n\r\n";
startPart += "YOUR_SECRET_TOKEN\r\n";
```

2. **Enable Certificate Validation:**
```cpp
// Instead of client.setInsecure(), use:
client.setCACert(root_ca);  // Add Cloudflare root certificate
```

3. **Encrypt Sensitive Data:**
- Store WiFi credentials in EEPROM
- Use HTTPS only (already implemented ✅)

---

## 📊 Data Flow

```
ESP32-CAM + DHT11
       ↓
   Read Sensors
       ↓
   Alert Condition?
       ↓ (Yes)
   Capture Image
       ↓
   HTTPS POST to Cloudflare Tunnel
       ↓
   Flask Backend (/iot/report)
       ↓
   ├─→ Update sensor_data
   ├─→ Log to MongoDB
   ├─→ Run YOLO Prediction
   └─→ Send Email Alerts
       ↓
   Flutter Dashboard Updates
```

---

## ✅ Success Checklist

- [ ] ESP32-CAM powered and connected
- [ ] DHT11 wired correctly
- [ ] Code uploaded successfully
- [ ] WiFi connected (check Serial Monitor)
- [ ] Server URL configured correctly
- [ ] Normal readings visible in Serial Monitor
- [ ] Dashboard shows real sensor data
- [ ] Alert test successful (heat sensor)
- [ ] Email notifications received
- [ ] Fire prediction working

---

## 🆘 Need Help?

**Check Serial Monitor for errors:**
- ❌ symbols indicate errors
- ✅ symbols indicate success
- Look for specific error messages

**Common Error Messages:**
- `Camera init failed 0x...` → Camera hardware issue
- `WiFi connection FAILED` → WiFi credentials wrong
- `Connection to server failed` → Server/tunnel issue
- `DHT11 read failed` → Sensor wiring issue

---

## 🎉 You're Done!

Your ESP32-CAM is now:
- ✅ Monitoring temperature & humidity
- ✅ Capturing images on alert
- ✅ Sending data to cloud backend
- ✅ Triggering automatic fire prediction
- ✅ Sending email alerts
- ✅ Updating dashboard in real-time

**Next Steps:**
- Deploy multiple ESP32 units for different rooms
- Add more sensors (smoke, CO2, etc.)
- Implement mobile push notifications
- Create alert history visualization
