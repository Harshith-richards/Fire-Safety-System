#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "DHT.h"

// ================== WIFI CONFIG ==================
const char* ssid       = "YOUR_WIFI_SSID";      // <- CHANGE THIS
const char* password   = "YOUR_WIFI_PASSWORD";  // <- CHANGE THIS

// ================== SERVER CONFIG (HTTPS) ==================
// Use your Cloudflare URL or public IP here
const char* serverHost = "  "; // <- CHANGE THIS to your local ip address, , if you are using the same network as the ESP32, or else you can host in cloudflare and host theri and replace it with cloudflare url

const int   serverPort = 443;                 // HTTPS port
const char* serverPath = "/iot/report";       // Flask IoT endpoint

// ================== CAMERA PINS (AI THINKER) ==================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ================== SENSORS ==================
#define DHTPIN    13
#define DHTTYPE   DHT11

// MQ2 Gas Sensor (Digital Pin)
// Connect MQ2 DO (Digital Output) to GPIO 14
#define MQ2_PIN   14 

DHT dht(DHTPIN, DHTTYPE);

// Alert thresholds
#define TEMP_ALERT_C     30.0   // fire-like temp
#define HUMIDITY_LOW_PCT  25.0  // very dry air

// Simple state
bool alertActive = false;
int  highCount   = 0;
int  lowCount    = 0;

// Retry configuration
#define MAX_RETRIES 3
#define RETRY_DELAY_MS 2000

// ================== INIT CAMERA ==================
bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size   = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 12;
    config.fb_count     = 2;
  } else {
    config.frame_size   = FRAMESIZE_QVGA;
    config.jpeg_quality = 15;
    config.fb_count     = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed 0x%x\n", err);
    return false;
  }
  Serial.println("✅ Camera initialized successfully");
  return true;
}

// ================== WIFI ==================
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.printf("Connecting to WiFi: %s\n", ssid);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 40) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("✅ WiFi connected. ESP32 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("❌ WiFi connection FAILED");
  }
}

// ================== HTTPS MULTIPART UPLOAD ==================
bool sendReportToServer(camera_fb_t* fb, float temp, float hum, float gasLevel, bool alertFlag) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected, cannot send report");
    return false;
  }

  WiFiClientSecure client;
  client.setInsecure(); // Skip certificate validation
  
  Serial.printf("📡 Connecting to %s:%d\n", serverHost, serverPort);
  
  if (!client.connect(serverHost, serverPort)) {
    Serial.println("❌ Connection to server failed");
    return false;
  }

  Serial.println("✅ Connected to server");

  String boundary = "----ESP32Boundary123456";
  String startPart = "";
  startPart += "--" + boundary + "\r\n";
  startPart += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
  startPart += "esp32_cam_dht11_mq2\r\n"; // THIS MUST MATCH USER'S REGISTERED DEVICE ID

  startPart += "--" + boundary + "\r\n";
  startPart += "Content-Disposition: form-data; name=\"temperature\"\r\n\r\n";
  startPart += String(temp, 1) + "\r\n";

  startPart += "--" + boundary + "\r\n";
  startPart += "Content-Disposition: form-data; name=\"humidity\"\r\n\r\n";
  startPart += String(hum, 1) + "\r\n";

  startPart += "--" + boundary + "\r\n";
  startPart += "Content-Disposition: form-data; name=\"gas_level\"\r\n\r\n";
  startPart += String(gasLevel, 1) + "\r\n";

  startPart += "--" + boundary + "\r\n";
  startPart += "Content-Disposition: form-data; name=\"alert\"\r\n\r\n";
  startPart += (alertFlag ? "1" : "0");
  startPart += "\r\n";

  // Image header
  String imgHeader = "";
  if (fb) {
      imgHeader += "--" + boundary + "\r\n";
      imgHeader += "Content-Disposition: form-data; name=\"image\"; filename=\"capture.jpg\"\r\n";
      imgHeader += "Content-Type: image/jpeg\r\n\r\n";
  }

  String endPart = "\r\n--" + boundary + "--\r\n";

  int contentLength = startPart.length() + endPart.length();
  if (fb) {
      contentLength += imgHeader.length() + fb->len;
  }

  // ---- HTTPS request header ----
  client.print(String("POST ") + serverPath + " HTTP/1.1\r\n");
  client.print(String("Host: ") + serverHost + "\r\n");
  client.print("Content-Type: multipart/form-data; boundary=" + boundary + "\r\n");
  client.print("Content-Length: " + String(contentLength) + "\r\n");
  client.print("Connection: close\r\n\r\n");

  // ---- Body: form fields + image ----
  client.print(startPart);
  
  if (fb) {
      client.print(imgHeader);
      // Send JPEG bytes in chunks
      const size_t chunkSize = 1024;
      size_t remaining = fb->len;
      size_t offset = 0;
      
      while (remaining > 0) {
        size_t toSend = (remaining > chunkSize) ? chunkSize : remaining;
        client.write(fb->buf + offset, toSend);
        offset += toSend;
        remaining -= toSend;
      }
  }

  client.print(endPart);

  Serial.println("📤 Report sent, waiting for response...");

  // Read response
  unsigned long timeout = millis();
  bool responseReceived = false;
  
  while (client.connected() && millis() - timeout < 10000) {
    while (client.available()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);
      responseReceived = true;
      timeout = millis();
    }
  }
  
  client.stop();
  Serial.println("🔌 Connection closed");
  
  return responseReceived;
}

// ================== SETUP ==================
void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n╔════════════════════════════════════════╗");
  Serial.println("║  Dr. Fire - IoT Node                   ║");
  Serial.println("║  ESP32-CAM + DHT11 + MQ2               ║");
  Serial.println("╚════════════════════════════════════════╝\n");

  if (!initCamera()) {
    Serial.println("❌ Camera init failed, restarting...");
    delay(1000);
    ESP.restart();
  }

  dht.begin();
  pinMode(MQ2_PIN, INPUT);
  
  Serial.println("✅ Sensors initialized (DHT11 + MQ2)");
  
  connectWiFi();
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected, restarting...");
    delay(1000);
    ESP.restart();
  }
  
  Serial.println("\n🚀 System ready! Monitoring environment...\n");
}

// ================== LOOP ==================
void loop() {
  static unsigned long lastRead = 0;
  if (millis() - lastRead < 1500) { // Read every 1.5 seconds
    return;
  }
  lastRead = millis();

  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠  WiFi disconnected, reconnecting...");
    connectWiFi();
    return;
  }

  // --- READ SENSORS ---
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  // Read MQ2 Digital Output
  // Usually LOW = Gas Detected (Active Low) for many modules
  int mq2State = digitalRead(MQ2_PIN);
  bool gasDetected = (mq2State == LOW); // Assuming Active Low
  
  // Convert to a "level" for backend (0 or 100)
  float gasLevel = gasDetected ? 100.0 : 10.0;

  if (isnan(h) || isnan(t)) {
    Serial.println("❌ DHT11 read failed");
    return;
  }

  Serial.print("🌡 Temp: "); Serial.print(t);
  Serial.print("°C | 💧 Hum: "); Serial.print(h);
  Serial.print("% | ⛽ Gas: "); 
  Serial.println(gasDetected ? "DETECTED!" : "Normal");

  bool tempCondition = (t >= TEMP_ALERT_C);
  bool humCondition  = (h <= HUMIDITY_LOW_PCT);
  bool gasCondition  = gasDetected;

  // Fire only if (Temp high OR Humidity low) AND Gas detected
  bool shouldAlert = ((tempCondition || humCondition) && gasCondition);

  if (!alertActive) {
    if (shouldAlert) {
      highCount++;
    } else {
      highCount = 0;
    }

    if (highCount >= 3) { // 3 consecutive readings to confirm
      alertActive = true;
      lowCount = 0;
      Serial.println("\n🚨 ═══════════════════════════════════════");
      Serial.println("   ALERT: Fire/Gas conditions detected!");
      Serial.println("   ═══════════════════════════════════════\n");

      // ---- Capture image ----
      camera_fb_t* fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("❌ Camera capture failed");
      } else {
        Serial.printf("📸 Image captured: %d bytes\n", fb->len);
        
        // ---- Send readings + image to Flask with retry ----
        bool success = false;
        for (int retry = 0; retry < MAX_RETRIES; retry++) {
          if (retry > 0) {
            Serial.printf("🔄 Retry attempt %d/%d\n", retry + 1, MAX_RETRIES);
            delay(RETRY_DELAY_MS);
          }
          
          success = sendReportToServer(fb, t, h, gasLevel, true);
          
          if (success) {
            Serial.println("✅ Alert sent successfully!");
            break;
          } else {
            Serial.println("❌ Failed to send alert");
          }
        }
        
        if (!success) {
          Serial.println("⚠  All retry attempts failed!");
        }
        
        esp_camera_fb_return(fb);
      }
    } else {
      Serial.println("✅ OK: Environment normal.");
      
      // Send normal status update (without image) every 30 seconds
      static unsigned long lastNormalUpdate = 0;
      if (millis() - lastNormalUpdate > 5000) {
        lastNormalUpdate = millis();
        
        // Send status without image
        sendReportToServer(NULL, t, h, gasLevel, false);
      }
    }
  } else {
    // Alert already active -> wait for safe condition
    if (!shouldAlert) {
      lowCount++;
    } else {
      lowCount = 0;
    }

    if (lowCount >= 3) { // needs longer safe period
      alertActive = false;
      highCount = 0;
      Serial.println("\n✅ ═══════════════════════════════════════");
      Serial.println("   ALERT CLEARED - Environment safe");
      Serial.println("   ═══════════════════════════════════════\n");
    } else {
      Serial.println("⚠  ALERT STILL ACTIVE (waiting to clear)...");
    }
  }

  Serial.println("─────────────────────────────────────────");
}
