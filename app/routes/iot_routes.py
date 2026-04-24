from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import os
import threading
import io
from PIL import Image

from ..config import Config
from ..database import users_collection, logs_collection
from ..services.iot_service import sensor_data, update_sensor_data, reset_alarm as service_reset_alarm
from ..services.yolo_service import yolo_model, predict_image
from ..services.email_service import send_fire_alert, send_sos_email

iot_bp = Blueprint('iot', __name__)

@iot_bp.route('/iot/report', methods=['POST'])
def iot_report():
    try:
        # Get form data
        device_id = request.form.get('device_id', 'unknown')
        temperature = float(request.form.get('temperature', 25.0))
        humidity = float(request.form.get('humidity', 50.0))
        gas_level = float(request.form.get('gas_level', 10.0))
        alert = request.form.get('alert', '0')
        alert_flag = (alert == '1' or alert.lower() == 'true')
        
        # Get image if present
        image_file = request.files.get('image')
        
        print(f"📡 IoT Report from {device_id}: Temp={temperature}°C, Humidity={humidity}%, Gas={gas_level}, Alert={alert_flag}")
        
        # Update global sensor data
        update_sensor_data(temperature, humidity, gas_level, device_id, alert_flag)
        
        # Save image if present and valid
        image_url = None
        if image_file and alert_flag:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"esp32_{timestamp}_{unique_id}.jpg"
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                
                image_file.save(filepath)
                image_url = f"/uploads/{filename}"
                print(f"💾 Image saved: {filepath}")
            except Exception as e:
                print(f"⚠️ Image save error: {e}")
        
        # Find user associated with this device
        user = users_collection.find_one({"device_id": device_id})
        user_email = user['email'] if user else None
        user_name = user['name'] if user else "IoT User"
        
        # Log to MongoDB
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "user_email": user_email,
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
                image_file.seek(0)
                image_bytes = image_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Run YOLO prediction
                result = predict_image(image)
                
                predicted_class = result['predicted_class']
                predicted_conf = result['predicted_confidence']
                recommendation = result['recommendation']
                
                print(f"✅ Prediction: {predicted_class} ({predicted_conf:.2f}%)")
                
                # Update sensor data with fire class
                update_sensor_data(temperature, humidity, 10.0, device_id, alert_flag, predicted_class)
                
                prediction_result = {
                    "predicted_class": predicted_class,
                    "confidence": round(predicted_conf, 2),
                    "recommendation": recommendation
                }
                
                # Add prediction to log entry
                log_entry['fire_class'] = predicted_class
                log_entry['confidence'] = round(predicted_conf, 2)
                log_entry['recommendation'] = recommendation
                
                # Send email notifications in background
                if user_email:
                     email_thread = threading.Thread(
                        target=send_fire_alert,
                        args=(user_email, user_name, predicted_class, recommendation)
                    )
                     email_thread.daemon = True
                     email_thread.start()
                     print("📧 Email notification queued")
                
            except Exception as e:
                print(f"❌ Prediction error: {e}")
                prediction_result = {"error": str(e)}
                log_entry['prediction_error'] = str(e)
        
        # Insert log to MongoDB
        logs_collection.insert_one(log_entry)
        
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

@iot_bp.route('/status', methods=['GET'])
def get_status():
    sensor_data['last_updated'] = datetime.now().isoformat()
    return jsonify(sensor_data), 200

@iot_bp.route('/reset_alarm', methods=['POST'])
def reset_alarm():
    service_reset_alarm()
    print("🔧 Alarm reset by admin")
    return jsonify({"message": "Alarm reset successfully"}), 200

@iot_bp.route('/sos', methods=['POST'])
def sos_alert():
    data = request.json
    email = data.get('email')
    location = data.get('location')
    
    if send_sos_email(email, location):
        return jsonify({"message": "SOS Alert Sent"}), 200
    else:
        return jsonify({"error": "Failed to send SOS"}), 500
