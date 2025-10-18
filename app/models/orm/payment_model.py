from app import db
from datetime import datetime

class PaymentModel(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    stripe_id = db.Column(db.String(255), nullable=False)   # Stripe payment ID
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(7), default="USD")
    stylist_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(12), nullable=False)     # failed or successful