from flask import Flask
from app.config import Config
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialise database
    db.init_app(app)

    # importing models here, so they are registered
    from app.models.orm import user_model, service_model, slot_model, appointment_model, payment_model

    with app.app_context():
        db.create_all()     # creates all tables if they don't exist yet, but it does not update existing tables (for that, we can use a migration library) 
    

    return app