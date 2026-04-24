from flask import Blueprint, request, jsonify
from ..database import users_collection
import random
from ..services.email_service import send_otp_email

auth_bp = Blueprint('auth', __name__)

otp_storage = {}

def generate_otp():
    return str(random.randint(100000, 999999))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
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
        "latitude": data.get('latitude'),
        "longitude": data.get('longitude')
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email, "password": password})
    if user:
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

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter required"}), 400
    
    user = users_collection.find_one({"email": email}, {'_id': 0, 'password': 0})
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    otp = generate_otp()
    otp_storage[email] = otp
    
    if send_otp_email(email, otp):
        return jsonify({"message": "OTP sent successfully to your email"}), 200
    else:
        return jsonify({"error": "Failed to send OTP"}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    
    if not email or not otp or not new_password:
        return jsonify({"error": "Email, OTP, and new password are required"}), 400
    
    if otp_storage.get(email) == otp:
        users_collection.update_one({"email": email}, {"$set": {"password": new_password}})
        del otp_storage[email]
        return jsonify({"message": "Password reset successfully"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 400

@auth_bp.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    email = data.get('email')
    
    update_fields = {}
    if 'first_name' in data: update_fields['first_name'] = data['first_name']
    if 'last_name' in data: update_fields['last_name'] = data['last_name']
    if 'phone' in data: update_fields['phone'] = data['phone']
    if 'address' in data: update_fields['address'] = data['address']
    if 'latitude' in data: update_fields['latitude'] = data['latitude']
    if 'longitude' in data: update_fields['longitude'] = data['longitude']
    
    if 'first_name' in data or 'last_name' in data:
        user = users_collection.find_one({"email": email})
        f_name = data.get('first_name', user.get('first_name', ''))
        l_name = data.get('last_name', user.get('last_name', ''))
        update_fields['name'] = f"{f_name} {l_name}".strip()

    users_collection.update_one({"email": email}, {"$set": update_fields})
    return jsonify({"message": "Profile updated successfully"}), 200
