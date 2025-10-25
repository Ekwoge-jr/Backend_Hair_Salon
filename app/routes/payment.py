from flask import Blueprint, request, jsonify
from app.integrations.stripe import create_payment_intent
from app import db
from app.models.orm.payment_model import PaymentModel

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/create-payment", methods=["POST"])
def create_payment():
    data = request.get_json()
    amount = data.get("amount")
    currency = data.get("currency", "usd")

    try:
        payment_intent = create_payment_intent(amount, currency)

        payment = PaymentModel(
        stripe_id=payment_intent["id"],
        amount=payment_intent["amount"] / 100,  # convert from cents
        currency=payment_intent["currency"],
        status=payment_intent["status"]
        )
        db.session.add(payment)
        db.session.commit()


        return jsonify(payment_intent), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
