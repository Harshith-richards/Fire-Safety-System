from flask import Blueprint, request, jsonify, send_from_directory
import os
from ..database import logs_collection
from ..config import Config

log_bp = Blueprint('log', __name__)

@log_bp.route('/logs', methods=['GET'])
def get_logs():
    email = request.args.get('email')
    if not email:
        return jsonify([]), 200
    
    # Filter logs by user email
    logs = list(logs_collection.find(
        {"user_email": email}, 
        {'_id': 0}
    ).sort("timestamp", -1).limit(50))
    
    return jsonify(logs), 200

@log_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.abspath(Config.UPLOAD_FOLDER), filename)
