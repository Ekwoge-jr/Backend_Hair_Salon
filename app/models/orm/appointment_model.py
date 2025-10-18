from app import db
from datetime import datetime

class AppointmentModel(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slots.id"), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    google_event_id = db.Column(db.String(255), nullable=False)     # Google Calendar event ID 
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    status = db.Column(db.String(10), default = "booked")     # booked, completed, cancelled