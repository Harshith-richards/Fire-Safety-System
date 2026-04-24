
#Replace all the demo gmail ids and passwords with actual ones before deploying.

# if you face issues with email sending, ensure that: you mail to this email ID harshithkvr@gmail.com




from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import threading
import time
import random
from datetime import datetime
import socket
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Image Upload Configuration ---
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"✅ Created uploads folder: {UPLOAD_FOLDER}")

# --- Configuration ---
# Connect to local MongoDB. Ensure MongoDB is running!
# Default port is 27017. Database name: 'fire_safety_db'
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['fire_safety_db']
    users_collection = db['users']
    logs_collection = db['logs']
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# --- YOLO Model Loading ---
try:
    from ultralytics import YOLO
    MODEL_PATH = "best.pt"
    if os.path.exists(MODEL_PATH):
        yolo_model = YOLO(MODEL_PATH)
        print(f"✅ YOLO model loaded successfully from {MODEL_PATH}")
    else:
        yolo_model = None
        print(f"⚠️ Warning: Model file '{MODEL_PATH}' not found. Prediction endpoint will not work.")
except Exception as e:
    yolo_model = None
    print(f"⚠️ Error loading YOLO model: {e}")

# --- Fire Type to Extinguisher Class Mapping ---
extinguisher_map = {
    "Class_A": [
        "cloth_burning_real_fire", "dry_leaves_burning_real_photo", "furniture_on_fire_real_photo",
        "garbage_fire_real_photo", "paper_on_fire_real_photo", "plastic_fire_real_scene",
        "rubber_burning_real_fire", "wood_on_fire_real_photo", "wood_real_photo"
    ],
    "Class_B": [
        "alcohol fire real photo", "diesel_fire_real_scene", "kerosene fire real image",
        "oil burning real photo", "petrol_fire_real_incident"
    ],
    "Class_C": [
        "battery explosion fire real photo", "circuit_board_on_fire_real_photo",
        "electrical fire real photo", "motor_on_fire_real_scene",
        "transformer fire incident", "wiring fire real incident"
    ],
    "Class_D": [
        "aluminium burning fire", "lithium battery fire real photo",
        "magnesium fire real photo", "potassium fire reaction",
        "sodium fire chemical reaction", "titanium burning real fire"
    ],
    "Class_K": [
        "cooking oil fire in kitchen", "grease fire real kitchen",
        "kitchen stove fire real scene", "pan on fire real photo",
        "restaurant fire in kitchen", "restaurant_fire_in_kitchen"
    ]
}

# --- Fire Extinguisher Recommendations ---
recommendations = {
    "Class_A": "Use WATER or FOAM extinguishers for wood, paper, or cloth fires.",
    "Class_B": "Use CO₂ or DRY POWDER extinguishers for flammable liquids like petrol or diesel.",
    "Class_C": "Use CO₂ or DRY POWDER extinguishers for electrical fires.",
    "Class_D": "Use SPECIAL DRY POWDER extinguishers for metal fires.",
    "Class_K": "Use WET CHEMICAL extinguishers for cooking oil and grease fires."
}

# --- Global State (Real IoT Sensors) ---
sensor_data = {
    "temperature": 25.0,
    "gas_level": 10.0,  # Dummy value for now
    "fire_class": "None",
    "image_url": "https://placeholder.com/safe.png",
    "alert_status": False,
    "humidity": 50.0,
    "last_updated": datetime.now().isoformat(),
    "device_id": "waiting_for_iot"
}

# --- Background Thread for Simulation ---
def simulate_sensors():
    global sensor_data
    while True:
        # Randomize values
        temp = round(random.uniform(20.0, 60.0), 2)
        gas = round(random.uniform(0.0, 100.0), 2)
        
        sensor_data["temperature"] = temp
        sensor_data["gas_level"] = gas
        
        # Logic to trigger alert
        if temp > 50.0 or gas > 80.0:
            sensor_data["alert_status"] = True
            sensor_data["fire_class"] = random.choice(["A", "B", "C"])
            sensor_data["image_url"] = "https://via.placeholder.com/300/FF0000/FFFFFF?text=FIRE+DETECTED"
            
            # Log the incident if it's a new alert (simple logic to avoid spamming logs)
            # In a real app, you'd check if an alert is already active before logging
            # For this demo, we'll just log it every time the simulation hits high values
            # To prevent log spam, let's check if we recently logged it? 
            # Actually, let's just log it. Admin can view history.
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "temperature": temp,
                "gas_level": gas,
                "fire_class": sensor_data["fire_class"],
                "status": "DANGER"
            }
            # Insert into MongoDB
            try:
                logs_collection.insert_one(log_entry)
            except Exception as e:
                print(f"Error logging incident: {e}")
                
        else:
            # Only reset if admin hasn't cleared it? 
            # The requirement says "reset_alarm" endpoint for Admin to turn off alert.
            # So the simulation shouldn't auto-turn off the alert_status if it was triggered?
            # OR, the simulation represents CURRENT sensor readings. 
            # If readings go back to normal, the DANGER might persist until reset?
            # Let's make it so: if readings are normal, status is SAFE, UNLESS 'alert_status' was latched.
            # But for simplicity in this demo, let's let the simulation drive the values, 
            # and the 'alert_status' boolean can be a latch that the Admin resets.
            
            # Let's say: if temp/gas are high -> alert_status = True.
            # If they drop, alert_status REMAINS True until Admin resets it.
            # BUT, if the simulation keeps running, it might re-trigger it.
            # Let's stick to: Simulation updates values. 
            # If values > threshold -> set alert_status = True.
            # If values < threshold -> we don't auto-reset alert_status to False. Admin does that.
            pass

        time.sleep(5)

# IoT endpoint - receives data from ESP32-CAM
@app.route('/iot/report', methods=['POST'])
def iot_report():
    """Receive sensor data and image from ESP32-CAM"""
    global sensor_data
    
    try:
        # Get form data
        device_id = request.form.get('device_id', 'unknown')
        temperature = float(request.form.get('temperature', 25.0))
        humidity = float(request.form.get('humidity', 50.0))
        alert = request.form.get('alert', '0')
        alert_flag = (alert == '1' or alert.lower() == 'true')
        
        # Get image if present
        image_file = request.files.get('image')
        
        print(f"📡 IoT Report from {device_id}: Temp={temperature}°C, Humidity={humidity}%, Alert={alert_flag}")
        
        # Update global sensor data
        sensor_data['temperature'] = temperature
        sensor_data['humidity'] = humidity
        sensor_data['gas_level'] = 10.0  # Dummy value for now
        sensor_data['device_id'] = device_id
        sensor_data['last_updated'] = datetime.now().isoformat()
        
        # FIX: Reset alert status if not alerting
        if not alert_flag:
            sensor_data['alert_status'] = False
            sensor_data['fire_class'] = "None"
        
        # Save image if present and valid
        image_url = None
        if image_file and alert_flag:
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"esp32_{timestamp}_{unique_id}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save image
                image_file.save(filepath)
                image_url = f"/uploads/{filename}"
                print(f"💾 Image saved: {filepath}")
            except Exception as e:
                print(f"⚠️ Image save error: {e}")
        
        # Find user associated with this device
        user = users_collection.find_one({"device_id": device_id})
        user_email = user['email'] if user else None
        
        # Log to MongoDB
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "user_email": user_email, # Tag log with user email
            "temperature": temperature,
            "humidity": humidity,
            "gas_level": sensor_data['gas_level'],
            "alert": alert_flag,
            "status": "DANGER" if alert_flag else "SAFE",
            "image_url": image_url
        }
        
        # If alert flag is set and image is present, run prediction
        prediction_result = None
        if alert_flag and image_file and yolo_model:
            print("🔥 Alert triggered! Running fire prediction...")
            
            try:
                # Read image for prediction
                image_file.seek(0)  # Reset file pointer
                image_bytes = image_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                print(f"✅ Image loaded: {image.size}")
                
                # Run YOLO prediction
                results = yolo_model.predict(source=image, verbose=False)
                
                # Get top-5 predictions
                top5 = results[0].probs.top5
                top5_conf = results[0].probs.top5conf.tolist()
                
                # Aggregate confidence per extinguisher class
                class_conf = {"Class_A": 0, "Class_B": 0, "Class_C": 0, "Class_D": 0, "Class_K": 0}
                
                for cls_id, conf in zip(top5, top5_conf):
                    class_name = results[0].names[cls_id]
                    for fire_class, names in extinguisher_map.items():
                        if class_name in names:
                            class_conf[fire_class] += conf
                
                # Determine most likely class
                predicted_class = max(class_conf, key=class_conf.get)
                predicted_conf = class_conf[predicted_class] * 100
                
                print(f"✅ Prediction: {predicted_class} ({predicted_conf:.2f}%)")
                
                # Update sensor data
                sensor_data['fire_class'] = predicted_class
                sensor_data['alert_status'] = True
                
                prediction_result = {
                    "predicted_class": predicted_class,
                    "confidence": round(predicted_conf, 2),
                    "recommendation": recommendations[predicted_class]
                }
                
                # Add prediction to log entry
                log_entry['fire_class'] = predicted_class
                log_entry['confidence'] = round(predicted_conf, 2)
                log_entry['recommendation'] = recommendations[predicted_class]
                
                # Send email notifications in background
                email_thread = threading.Thread(
                    target=send_email_notification,
                    args=("demo@gmail.com", "IoT User", predicted_class, recommendations[predicted_class])
                )
                #Replace with actual user email
                email_thread.daemon = True
                email_thread.start()
                print("📧 Email notification queued")
                
            except Exception as e:
                print(f"❌ Prediction error: {e}")
                prediction_result = {"error": str(e)}
                log_entry['prediction_error'] = str(e)
        
        # Insert log to MongoDB
        logs_collection.insert_one(log_entry)
        
        # Return response
        response = {
            "status": "success",
            "message": "Data received",
            "temperature": temperature,
            "humidity": humidity,
            "alert_processed": alert_flag,
            "image_saved": image_url is not None
        }
        
        if prediction_result:
            response['prediction'] = prediction_result
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ IoT report error: {e}")
        return jsonify({"error": str(e)}), 500

# Static file serving for uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/logs', methods=['GET'])
def get_logs():
    # Filter by user email if provided
    email = request.args.get('email')
    query = {}
    if email:
        query['user_email'] = email
        
    logs = list(logs_collection.find(query, {'_id': 0}).sort("timestamp", -1).limit(50))
    return jsonify(logs), 200

# --- Auth & User Endpoints ---

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    # Support both old 'name' and new 'first_name'/'last_name'
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    name = data.get('name', f"{first_name} {last_name}".strip())
    
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    phone = data.get('phone', '')
    address = data.get('address', '')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    user = {
        "name": name,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password, # In production, HASH this!
        "phone": phone,
        "address": address,
        "role": role,
        "device_id": data.get('device_id', 'unknown'), # Link user to device
        "latitude": data.get('latitude'),
        "longitude": data.get('longitude')
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user') # Optional check

    user = users_collection.find_one({"email": email, "password": password})
    if user:
        # Return user details including new fields
        return jsonify({
            "message": "Login successful",
            "role": user.get('role', 'user'),
            "name": user.get('name', ''),
            "email": user.get('email', ''),
            "phone": user.get('phone', ''),
            "address": user.get('address', ''),
            "first_name": user.get('first_name', ''),
            "last_name": user.get('last_name', '')
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/status', methods=['GET'])
def get_status():
    # Update timestamp
    sensor_data['last_updated'] = datetime.now().isoformat()
    return jsonify(sensor_data), 200

@app.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile by email"""
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter required"}), 400
    
    user = users_collection.find_one({"email": email}, {'_id': 0, 'password': 0})
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404

# --- Enhanced Features Endpoints ---

otp_storage = {} # Temporary in-memory storage for OTPs

def generate_otp():
    return str(random.randint(100000, 999999))

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    otp = generate_otp()
    otp_storage[email] = otp
    
    # Send OTP via Email
    sender_email = "demo@gmail.com"
    #Replace with actual sender email
    sender_password = "xx16-digitxx"
    #Replace with actual app password which is 16 characters long ,not your normal gmail password.
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = "Password Reset OTP"
    msg.attach(MIMEText(f"Your OTP for password reset is: {otp}", "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return jsonify({"error": "Failed to send OTP"}), 500

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    
    if otp_storage.get(email) == otp:
        users_collection.update_one({"email": email}, {"$set": {"password": new_password}})
        del otp_storage[email]
        return jsonify({"message": "Password reset successfully"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 400

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    email = data.get('email')
    
    update_fields = {}
    if 'first_name' in data: update_fields['first_name'] = data['first_name']
    if 'last_name' in data: update_fields['last_name'] = data['last_name']
    if 'phone' in data: update_fields['phone'] = data['phone']
    if 'address' in data: update_fields['address'] = data['address']
    
    # Update 'name' composite field if first/last changed
    if 'first_name' in data or 'last_name' in data:
        user = users_collection.find_one({"email": email})
        f_name = data.get('first_name', user.get('first_name', ''))
        l_name = data.get('last_name', user.get('last_name', ''))
        update_fields['name'] = f"{f_name} {l_name}".strip()

    users_collection.update_one({"email": email}, {"$set": update_fields})
    return jsonify({"message": "Profile updated successfully"}), 200

@app.route('/sos', methods=['POST'])
def sos_alert():
    data = request.json
    email = data.get('email')
    location = data.get('location')
    
    # Send SOS Email
    sender_email = "demo@gmail.com"
    #Replace with actual sender email
    sender_password = "xx16-digitxx"
    #Replace with actual app password which is 16 characters long ,not your normal gmail password.

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = "demo@gmail.com" # Send to admin/emergency contact , Replace with actual emergency contact email
    msg["Subject"] = "🚨 SOS EMERGENCY ALERT 🚨"
    body = f"SOS Alert received from user: {email}\nLocation: {location}\nPlease send help immediately!"
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return jsonify({"message": "SOS Alert Sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Email Notification Function ---
def send_email_notification(user_email, user_name, predicted_class, recommendation):
    """Send email notification to user when fire is detected"""
    sender_email = "demo@gmail.com" 
    #Replace with actual sender email
    sender_password = "xx16-digitxx"
    #Replace with actual app password which is 16 characters long ,not your normal gmail password.
    emergency_responder = "demo@gmail.com"  # Emergency responder email
    
    # Email to user
    subject_user = f"🔥 Fire Alert: {predicted_class} Detected!"
    body_user = f"""
    🚨 FIRE ALERT 🚨
    
    Dear {user_name},
    
    Fire Class Detected: {predicted_class}
    Recommendation: {recommendation}
    
    Immediate action required!
    Please use the appropriate fire extinguisher as recommended.
    
    Stay Safe!
    IoT Fire Safety System
    """
    
    # Email to emergency responders
    subject_emergency = f"🚨 EMERGENCY: {predicted_class} Fire Detected - User: {user_name}"
    body_emergency = f"""
    🚨 EMERGENCY FIRE ALERT 🚨
    
    Fire Class Detected: {predicted_class}
    User: {user_name}
    User Email: {user_email}
    
    Recommendation: {recommendation}
    
    IMMEDIATE RESPONSE REQUIRED!
    
    IoT Fire Safety System
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send to user
            msg_user = MIMEMultipart()
            msg_user["From"] = sender_email
            msg_user["To"] = user_email
            msg_user["Subject"] = subject_user
            msg_user.attach(MIMEText(body_user, "plain"))
            server.send_message(msg_user)
            print(f"✅ Email notification sent to user: {user_email}")
            
            # Send to emergency responder
            msg_emergency = MIMEMultipart()
            msg_emergency["From"] = sender_email
            msg_emergency["To"] = emergency_responder
            msg_emergency["Subject"] = subject_emergency
            msg_emergency.attach(MIMEText(body_emergency, "plain"))
            server.send_message(msg_emergency)
            print(f"✅ Emergency notification sent to: {emergency_responder}")
            
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

@app.route('/predict', methods=['POST'])
def predict_fire_class():
    """Predict fire class from uploaded image using YOLO model"""
    if yolo_model is None:
        return jsonify({"error": "YOLO model not loaded. Please ensure best.pt exists."}), 500
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Get user email from request (optional)
    user_email = request.form.get('user_email')
    user_name = request.form.get('user_name', 'User')
    
    try:
        # Read image
        print(f"📸 Received image: {file.filename}")
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        print(f"✅ Image loaded successfully: {image.size}")
        
        # Run YOLO prediction
        print("🔥 Running YOLO prediction...")
        results = yolo_model.predict(source=image, verbose=False)
        print("✅ YOLO prediction complete")
        
        # Get top-5 predictions
        top5 = results[0].probs.top5
        top5_conf = results[0].probs.top5conf.tolist()
        
        # Build top-5 list
        top5_predictions = []
        for i, (cls_id, conf) in enumerate(zip(top5, top5_conf)):
            class_name = results[0].names[cls_id]
            top5_predictions.append({
                "rank": i + 1,
                "fire_type": class_name,
                "confidence": round(conf * 100, 2)
            })
        
        # Aggregate confidence per extinguisher class
        class_conf = {"Class_A": 0, "Class_B": 0, "Class_C": 0, "Class_D": 0, "Class_K": 0}
        
        for cls_id, conf in zip(top5, top5_conf):
            class_name = results[0].names[cls_id]
            for fire_class, names in extinguisher_map.items():
                if class_name in names:
                    class_conf[fire_class] += conf
        
        # Round confidence values
        for k in class_conf:
            class_conf[k] = round(class_conf[k], 4)
        
        # Determine most likely class
        predicted_class = max(class_conf, key=class_conf.get)
        predicted_conf = class_conf[predicted_class] * 100
        
        # Get top-1 prediction
        top1_class = results[0].names[top5[0]]
        top1_conf = top5_conf[0] * 100
        
        # Send email notification asynchronously if user email is provided
        email_sent = False
        if user_email:
            # Send emails in background thread to not block response
            email_thread = threading.Thread(
                target=send_email_notification,
                args=(user_email, user_name, predicted_class, recommendations[predicted_class])
            )
            email_thread.daemon = True
            email_thread.start()
            email_sent = True  # Mark as sent (in progress)
            print(f"📧 Email notification queued for {user_email}")
        
        # Return results immediately
        response_data = {
            "success": True,
            "top1_fire_type": top1_class,
            "top1_confidence": round(top1_conf, 2),
            "predicted_class": predicted_class,
            "predicted_confidence": round(predicted_conf, 2),
            "class_confidences": class_conf,
            "recommendation": recommendations[predicted_class],
            "top5_predictions": top5_predictions,
            "email_sent": email_sent
        }
        
        print(f"✅ Prediction complete: {predicted_class} ({predicted_conf:.2f}%)")
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/reset_alarm', methods=['POST'])
def reset_alarm():
    """Reset the alarm status (admin only)"""
    global sensor_data
    sensor_data["alert_status"] = False
    sensor_data["fire_class"] = "None"
    print("🔧 Alarm reset by admin")
    return jsonify({"message": "Alarm reset successfully"}), 200

# --- Helper to print IP ---
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    # Sensor simulation disabled - using real IoT data
    # sensor_thread = threading.Thread(target=simulate_sensors, daemon=True)
    # sensor_thread.start()
    print("⚠️  Sensor simulation DISABLED - waiting for real IoT data from ESP32-CAM")
    
    ip = get_ip_address()
    print(f"Server running on http://{ip}:5000")
    print(f"Make sure to update your Flutter app's baseUrl to: http://{ip}:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
