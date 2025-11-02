from app import db

class AppointmentTokenModel(db.Model):
    __tablename__ = "appointment_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)     # the generated token
    expires_at = db.Column(db.DateTime, nullable=False)