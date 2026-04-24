from flask import Blueprint, request, jsonify
import threading
import io
from PIL import Image
from ..services.yolo_service import yolo_model, predict_image
from ..database import users_collection
from ..services.email_service import send_fire_alert

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/predict', methods=['POST'])
def predict_fire_class():
    if yolo_model is None:
        return jsonify({"error": "YOLO model not loaded"}), 500
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    user_email = request.form.get('user_email')
    user_name = request.form.get('user_name', 'User')
    
    try:
        print(f"📸 Received image: {file.filename}")
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        print("🔥 Running YOLO prediction...")
        result = predict_image(image)
        print("✅ YOLO prediction complete")
        
        email_sent = False
        if user_email:
            # Fetch user details for emergency contact
            user = users_collection.find_one({"email": user_email})
            phone = user.get('phone') if user else None
            address = user.get('address') if user else None
            latitude = user.get('latitude') if user else None
            longitude = user.get('longitude') if user else None

            email_thread = threading.Thread(
                target=send_fire_alert,
                args=(user_email, user_name, result['predicted_class'], result['recommendation'], phone, address, latitude, longitude)
            )
            email_thread.daemon = True
            email_thread.start()
            email_sent = True
            print(f"📧 Email notification queued for {user_email}")
        
        response_data = {
            "success": True,
            "top1_fire_type": result['names'][result['top5_ids'][0]],
            "top1_confidence": round(result['top5_confs'][0] * 100, 2),
            "predicted_class": result['predicted_class'],
            "predicted_confidence": round(result['predicted_confidence'], 2),
            "class_confidences": result['class_confidences'],
            "recommendation": result['recommendation'],
            "email_sent": email_sent
        }

        # SAVE LOG TO DATABASE
        from ..database import logs_collection
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_email": user_email,
            "status": "DANGER" if result['predicted_class'] != "Normal" else "NORMAL",
            "fire_class": result['predicted_class'],
            "confidence": round(result['predicted_confidence'], 2),
            "recommendation": result['recommendation'],
            "temperature": "N/A", # Not available from image
            "humidity": "N/A",    # Not available from image
            "gas_level": "N/A",   # Not available from image
            "image_url": "",      # TODO: Save image URL if needed, currently just processing bytes
            "source": "manual_prediction"
        }
        logs_collection.insert_one(log_entry)
        print("✅ Prediction saved to history logs")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
