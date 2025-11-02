from flask import Blueprint, request, jsonify
from app.integrations.stripe import create_payment_intent
from app import db

from app.models.repositories.payment_repo import PaymentRepository
from app.services.payment_service import PaymentService

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/create-payment", methods=["POST"])
def create_payment():
    data = request.get_json()
    amount = data.get("amount")
    currency = data.get("currency", "usd")

    client_id = data.get("client_id")
    service_id = data.get("service_id")
    slot_id = data.get("slot_id")

    metadata={
        "client_id": client_id,
        "service_id": service_id,
        "slot_id": slot_id
    }


    try:
        
        return PaymentService.create_payment(amount, currency, metadata)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
