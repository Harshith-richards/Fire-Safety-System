# Quick Testing Guide - Doctor Fire

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd e:\antigravity
python run.py
```
Backend should be running on `http://localhost:5000`

### 2. Run the Flutter App
```bash
flutter run
```

## 🧪 Testing New Features

### Feature 1: Location Accuracy

#### Test Registration with Location
1. Open the app and tap "Create Account"
2. Fill in your details
3. Tap "Get Current Location" button
4. **Expected**: Address field populates automatically
5. Complete registration
6. **Verify**: User profile shows correct address

#### Test Location Update
1. Login to the app
2. Navigate to Profile tab
3. Tap "Update Location" button
4. **Expected**: Address updates to current location
5. **Verify**: New address is saved

### Feature 2: SOS Alert with GPS

#### Test SOS Button
1. Login to the app
2. Go to Dashboard
3. Tap "SOS Alert" button
4. **Expected**: 
   - Success message appears
   - Email sent to emergency contact
5. **Verify Email Contains**:
   - Actual GPS coordinates (not 0.0, 0.0)
   - Google Maps link
   - User's phone and address

### Feature 3: Forgot Password

#### Test Password Reset Flow
1. On login screen, tap "Forgot Password?"
2. Enter your registered email
3. Tap "Send OTP"
4. **Expected**: OTP sent to email
5. Check your email for OTP code
6. Enter OTP and new password
7. Tap "Reset Password"
8. **Expected**: Success message, navigate to login
9. Login with new password
10. **Verify**: Login successful

### Feature 4: UI Improvements

#### Test Dashboard Layout
1. Login and view dashboard
2. **Check**:
   - Sensor cards don't overlap
   - All text is visible
   - Device ID displays correctly
   - Temperature graph shows below sensors
3. Rotate device (if on mobile)
4. **Verify**: Layout remains correct

### Feature 5: App Name

#### Verify App Name
1. Check app launcher
2. **Expected**: Shows "Doctor Fire"
3. Check login screen
4. **Expected**: Title shows "Doctor Fire"

## 🐛 Common Issues & Solutions

### Issue: Location Permission Denied
**Solution**: 
- Android: Go to Settings > Apps > Doctor Fire > Permissions > Enable Location
- iOS: Go to Settings > Doctor Fire > Location > While Using the App

### Issue: SOS shows 0.0 coordinates
**Possible Causes**:
1. Location permission not granted
2. GPS not enabled on device
3. Indoor location (weak GPS signal)

**Solution**: 
- Enable location permissions
- Go outdoors or near window
- Wait a few seconds for GPS lock

### Issue: OTP not received
**Possible Causes**:
1. Email service not configured
2. Email in spam folder
3. Invalid email address

**Solution**:
- Check spam/junk folder
- Verify email configuration in backend
- Check backend logs for errors

### Issue: "Get Current Location" button not working
**Solution**:
1. Check location permissions
2. Restart the app
3. Check console for error messages
4. Verify geolocator package is installed: `flutter pub get`

## 📱 Testing on Physical Device

### Build APK
```bash
flutter build apk --release
```
APK location: `build/app/outputs/flutter-apk/app-release.apk`

### Install on Android
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Important: Update baseUrl
Before building for device testing, update `lib/utils/constants.dart`:
```dart
// Replace localhost with your computer's IP address
const String baseUrl = 'http://192.168.1.XXX:5000';
```

To find your IP:
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

## 🔍 Debugging

### View Flutter Logs
```bash
flutter logs
```

### View Backend Logs
Check the terminal where `python run.py` is running

### Test API Endpoints Directly

#### Test Forgot Password
```bash
curl -X POST http://localhost:5000/forgot-password \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"your@email.com\"}"
```

#### Test SOS Alert
```bash
curl -X POST http://localhost:5000/sos \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"your@email.com\",\"location\":\"Test Location\"}"
```

## ✅ Feature Checklist

- [ ] Registration with GPS location works
- [ ] Profile location update works
- [ ] SOS sends correct GPS coordinates
- [ ] SOS email includes Google Maps link
- [ ] Forgot password sends OTP
- [ ] Password reset works with OTP
- [ ] Dashboard sensors don't overlap
- [ ] App name shows as "Doctor Fire"
- [ ] All permissions granted
- [ ] Tested on physical device

## 📞 Emergency Contact Configuration

Make sure to set the emergency email in `app/config.py`:
```python
EMERGENCY_EMAIL = 'emergency@example.com'
```

This email will receive all SOS alerts and fire detection notifications.

---

**Happy Testing! 🔥**
