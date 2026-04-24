import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    MONGO_URI = 'mongodb://localhost:27017/'
    DB_NAME = 'fire_safety_db'
    MODEL_PATH = "best.pt"
    
    # Email Config
    SENDER_EMAIL = "your-email@gmail.com"
    SENDER_PASSWORD = "your-app-password"
    EMERGENCY_EMAIL = "emergency-contact@gmail.com"

    # Maps and Recommendations
    EXTINGUISHER_MAP = {
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

    RECOMMENDATIONS = {
        "Class_A": "Use WATER or FOAM extinguishers for wood, paper, or cloth fires.",
        "Class_B": "Use CO₂ or DRY POWDER extinguishers for flammable liquids like petrol or diesel.",
        "Class_C": "Use CO₂ or DRY POWDER extinguishers for electrical fires.",
        "Class_D": "Use SPECIAL DRY POWDER extinguishers for metal fires.",
        "Class_K": "Use WET CHEMICAL extinguishers for cooking oil and grease fires."
    }

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
