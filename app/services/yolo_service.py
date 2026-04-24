import os
from ..config import Config

yolo_model = None

try:
    from ultralytics import YOLO
    if os.path.exists(Config.MODEL_PATH):
        yolo_model = YOLO(Config.MODEL_PATH)
        print(f"✅ YOLO model loaded successfully from {Config.MODEL_PATH}")
    else:
        print(f"⚠️ Warning: Model file '{Config.MODEL_PATH}' not found.")
except Exception as e:
    print(f"⚠️ Error loading YOLO model: {e}")

def predict_image(image):
    if not yolo_model:
        raise Exception("YOLO model not loaded")
    
    results = yolo_model.predict(source=image, verbose=False)
    
    # Get top-5 predictions
    top5 = results[0].probs.top5
    top5_conf = results[0].probs.top5conf.tolist()
    
    # Aggregate confidence per extinguisher class
    class_conf = {"Class_A": 0, "Class_B": 0, "Class_C": 0, "Class_D": 0, "Class_K": 0}
    
    for cls_id, conf in zip(top5, top5_conf):
        class_name = results[0].names[cls_id]
        for fire_class, names in Config.EXTINGUISHER_MAP.items():
            if class_name in names:
                class_conf[fire_class] += conf
    
    # Determine most likely class
    predicted_class = max(class_conf, key=class_conf.get)
    predicted_conf = class_conf[predicted_class] * 100
    
    return {
        "predicted_class": predicted_class,
        "predicted_confidence": predicted_conf,
        "class_confidences": class_conf,
        "recommendation": Config.RECOMMENDATIONS[predicted_class],
        "top5_ids": top5,
        "top5_confs": top5_conf,
        "names": results[0].names
    }
