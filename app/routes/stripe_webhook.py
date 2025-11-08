# app/routes/stripe_webhook.py
from flask import Blueprint, request, jsonify
import stripe
import os
from app.models.repositories.payment_repo import PaymentRepository
from app.services.appointment_service import AppointmentService
from app.services.service_service import ServiceService
from datetime import datetime
import pytz

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
        metadata = payment_intent.get("metadata", {})
        
        stripe_id = payment_intent["id"]
        client_email = metadata.get("client_email")
        full_name = metadata.get("full_name")
        phone_number = metadata.get("phone_number")
        service_id = int(metadata.get("service_id"))
        slot_id = int(metadata.get("slot_id"))
        start_time_str = metadata.get("start_time")

        # --- Convert start_time to datetime if present ---
        start_time = None
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                if start_time.tzinfo is None:
                    start_time = pytz.UTC.localize(start_time)
            except Exception:
                print("Invalid start_time format in metadata")
        

        # Update payment in DB
        PaymentRepository.update_status(id=stripe_id, status="succeeded")
        try:
            # Trigger the appointment creation
            AppointmentService.book_appointment(client_email=client_email, 
                                                full_name=full_name, 
                                                phone_number=phone_number, 
                                                service_id=service_id, 
                                                slot_id=slot_id, 
                                                stripe_id=stripe_id, 
                                                client_start_time=start_time
                                                )
            print("✅ Appointment successfully booked:")
        except Exception as e:
            print(f"❌ Error while booking appointment: {e}")

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        PaymentRepository.update_status(payment_intent["id"], "failed")
        print("❌ Payment failed")

    return jsonify({"status": "success"}), 200
