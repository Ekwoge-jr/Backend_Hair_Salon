from flask import Flask
from flasgger import Swagger  # used to expose the API endpoints
from app.config import Config
from app.database import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager  # for jwt authentication
import os


bcrypt = Bcrypt()   


from app.routes.payment import payment_bp
from app.routes.calendar import calendar_bp

from app.routes.user import user_bp
from app.routes.stripe_webhook import stripe_webhook_bp

from app.routes.appointment import appointment_bp
from app.routes.service import service_bp
from app.routes.auth import auth_bp
from app.routes.slot import slot_bp


jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # Set secret key (use .env)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 2592000  # 30 days

    # Initialise JWT
    jwt.init_app(app)


    # initialise database
    db.init_app(app)

    # initialise bcrypt
    bcrypt.init_app(app)


    app.config["SWAGGER"] = {
        "title": "Hair Salon Booking API",
        "uiversion": 3
    }

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
    
    return app