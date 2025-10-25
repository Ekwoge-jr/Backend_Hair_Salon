from app import db
from datetime import datetime

class PaymentModel(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    stripe_id = db.Column(db.String(255), nullable=False)   # Stripe payment ID
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(7), default="USD")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(102), nullable=False)     