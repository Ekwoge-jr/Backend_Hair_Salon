from flask import Flask
from app.config import Config
from app.database import db

from app.routes.payment import payment_bp
from app.routes.calendar import calendar_bp
from app.routes.test import user_bp
from app.routes.stripe_webhook import stripe_webhook_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialise database
    db.init_app(app)

    # importing models here, so they are registered
    from app.models.orm import user_model, service_model, slot_model, appointment_model, payment_model

    with app.app_context():
        db.create_all()     # creates all tables if they don't exist yet, but it does not update existing tables (for that, we can use a migration library) 
    
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(calendar_bp, url_prefix="/api/calendar")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(stripe_webhook_bp, url_prefix="/api")
    return app