# 🌐 Global Access Setup Guide - IoT Fire Safety Application

This guide will help you make your Flask backend and Flutter frontend accessible from anywhere in the world **without purchasing a domain name**.

## 🚀 Quick Start (Cloudflare Tunnel)

> **Recommended for production use** - Free, stable, and permanent URLs.

### Step 1: Download Cloudflare Tunnel
1. Download `cloudflared` for Windows:
   `https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe`
2. Rename the downloaded file to `cloudflared.exe`.
3. Move it to a convenient location (e.g., `C:\cloudflared\cloudflared.exe`).

### Step 2: Start Your Flask Backend
1. Open **Command Prompt** or **PowerShell**.
2. Navigate to your project directory:
   ```powershell
   cd "d:\final b9"
   ```
3. Activate your virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
4. Start the Flask server:
   ```powershell
   python run.py
   ```
   *Note: Ensure your email credentials in `app/config.py` are correct.*

### Step 3: Create Cloudflare Tunnel
1. Open a **NEW** Command Prompt or PowerShell window.
2. Navigate to where you saved `cloudflared.exe` (e.g., `cd C:\cloudflared`).
3. Run the tunnel command:
   ```powershell
   .\cloudflared.exe tunnel --url http://localhost:5000
   ```
4. Copy the generated URL (e.g., `https://random-words-1234.trycloudflare.com`). **This is your permanent public backend URL.**

### Step 4: Update Flutter App
1. Open `lib/utils/constants.dart` in your code editor.
2. Update the `baseUrl`:
   ```dart
   const String baseUrl = 'https://random-words-1234.trycloudflare.com';
   ```
3. Save the file and rebuild the app (Windows or APK).

---

## 🔄 Alternative Methods

### Option A: ngrok
1. Download and authenticate `ngrok`.
2. Start your backend on port 5000.
3. Run: `.\ngrok.exe http 5000`.
4. Copy the HTTPS URL and update `baseUrl` in `lib/utils/constants.dart`.

---

## ✅ Testing & Verification

1. **Test Backend**: Visit `https://your-tunnel-url.trycloudflare.com/status` in a browser. You should see the sensor JSON.
2. **Test App**: Open the app from a different network (e.g., mobile data) and check if data updates.

---

## 🔧 Troubleshooting

- **Connection Error**: Ensure both `run.py` and the tunnel terminal are kept open.
- **Trailing Spaces**: Ensure there are no spaces when pasting the URL in `constants.dart`.
- **Database**: Ensure MongoDB is running locally (`net start MongoDB`).

---

**Safe Monitoring from Anywhere! 🔥🚨**
