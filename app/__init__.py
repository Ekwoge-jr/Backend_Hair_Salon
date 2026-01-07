from flask import Flask, send_from_directory
from flasgger import Swagger  # used to expose the API endpoints
from app.config import Config
from app.database import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager  # for jwt authentication
import os

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from flask_migrate import Migrate  # added this for migration (7/12/25) ################### (pip install Flask-Migrate)

bcrypt = Bcrypt()   

from app.routes.payment import payment_bp
from app.routes.calendar import calendar_bp

from app.routes.user import user_bp
from app.routes.stripe_webhook import stripe_webhook_bp

from app.routes.appointment import appointment_bp
from app.routes.service import service_bp
from app.routes.auth import auth_bp
from app.routes.slot import slot_bp

from flask_cors import CORS #added



migrate = Migrate()  ## added this (7/12/25) ###########################

# from julius

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'services')

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # from julius
    # CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}}) # 

    CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Headers"],
    "supports_credentials": True
}})

    app.config.from_object(Config)


    # Set secret key (use .env)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 2592000  # 30 days

    # Initialise JWT
    jwt.init_app(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # This converts your dictionary {"id": 1, "role": "admin"} 
        # into a JSON string so the library is happy.
        import json
        return json.dumps(user)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        # This allows get_jwt_identity() to return the dictionary back to you
        import json
        identity = jwt_data["sub"]
        return json.loads(identity)


    # initialise database
    db.init_app(app)


    migrate.init_app(app, db)    ### added #############################################


    # initialise bcrypt
    bcrypt.init_app(app)


    app.config["SWAGGER"] = {
        "title": "Hair Salon Booking API",
        "uiversion": 3
    }


    # from julius
    
    # added the next 9 lines
    app.config['SERVICE_UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure folder exist
    
    # 2. Add the route to serve the uploaded files publicly
    @app.route('/uploads/services/<filename>')
    def uploaded_file(filename):
        # Serve the file from the configured folder
        return send_from_directory(app.config['SERVICE_UPLOAD_FOLDER'], filename)
    


    Swagger(app)   # ✅ attach swagger/openapi


    # importing models here, so they are registered
    from app.models.orm import user_model, service_model, slot_model, appointment_model, payment_model

    with app.app_context():
        db.create_all()     # creates all tables if they don't exist yet, but it does not update existing tables (for that, we can use a migration library) 
    
    app.register_blueprint(stripe_webhook_bp, url_prefix="/api")    # for the stripe webhook endpoint
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(appointment_bp, url_prefix="/api/appointment")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(service_bp, url_prefix="/api/service")
    app.register_blueprint(slot_bp, url_prefix="/api/slot")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")


    app.register_blueprint(calendar_bp, url_prefix="/api/calendar")

    @app.errorhandler(Exception)
    def handle_exception(e):
        # 1. Capture Database-specific errors
        if isinstance(e, SQLAlchemyError):
            return jsonify({
                "code": 500,
                "type": "DatabaseError",
                "error": str(e.__dict__.get('orig', e)), # Extracts the raw SQL error
                "message": "The database rejected this request."
            }), 500

        # 2. Capture standard HTTP errors (404, 403, etc)
        if isinstance(e, HTTPException):
            return jsonify({
                "code": e.code,
                "error": e.description,
            }), e.code

        # 3. Capture all other Python crashes
        return jsonify({
            "code": 500,
            "type": "PythonError",
            "error": str(e)
        }), 500
    
    return app