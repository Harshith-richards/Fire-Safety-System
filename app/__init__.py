from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.iot_routes import iot_bp
    from .routes.log_routes import log_bp
    from .routes.prediction_routes import prediction_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(iot_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(prediction_bp)
    
    return app
