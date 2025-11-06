# app/routes/stripe_webhook.py
from flask import Blueprint, request, jsonify
import stripe
import os
from app.models.repositories.payment_repo import PaymentRepository
from app.services.appointment_service import AppointmentService
from app.services.service_service import ServiceService

stripe_webhook_bp = Blueprint("stripe_webhook_bp", __name__)

# Set the Stripe secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# The webhook secret from Stripe Dashboard (used for signature verification)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@stripe_webhook_bp.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Verify this request actually came from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )

    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    # Handle specific event types
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        metadata = payment_intent["metadata"]

        stripe_id = payment_intent["id"]
        client_email = metadata["client_email"]

        full_name = metadata["full_name"]
        phone_number = metadata["phone_number"]

        service_id = metadata["service_id"]
        slot_id = metadata["slot_id"]
        

        #stripe_id = "pi_3SNwXeLrBwVmxIzX0iI8LTBI"
        #client_id = 2
        #service_id = 1
        #slot_id = 1
        

        # Update payment in DB
        PaymentRepository.update_status(stripe_id, "succeeded")

        # Trigger the appointment creation
        AppointmentService.book_appointment(client_email, full_name, phone_number, service_id, slot_id, stripe_id)


    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        PaymentRepository.update_status(payment_intent["id"], "failed")
        print("❌ Payment failed")

    return jsonify({"status": "success"}), 200
