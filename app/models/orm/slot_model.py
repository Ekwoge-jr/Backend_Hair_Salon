from app import db
from datetime import datetime

class SlotModel(db.Model):
    __tablename__ = "slots"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    start_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    end_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    date = db.Column(db.Date, nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)  # added
    status = db.Column(db.String(12), default="available")     # available, booked, expired