from flask import Blueprint, request, jsonify
from app.integrations.stripe import create_payment_intent
from app import db
import re
from app.models.repositories.payment_repo import PaymentRepository
from app.services.payment_service import PaymentService
from flasgger import swag_from
from datetime import datetime, timezone
import pytz


payment_bp = Blueprint("payment_bp", __name__)


@payment_bp.route("/create-payment", methods=["POST"])
def create_payment():


    """
    Create a Stripe payment intent
    ---
    tags:
      - Payments
    description: This endpoint creates a payment intent using Stripe and stores the payment metadata.
    consumes:
          - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              example: 5000
              description: Amount in smallest currency unit (e.g., cents)
            currency:
              type: string
              example: usd
              description: Currency code
            client_email:
              type: string
              example: johndoe@example.com
            full_name:
              type: string
              example: John Doe
            phone_number:
              type: string
              example: "+237678123456"
            service_id:
              type: integer
              example: 1
            slot_id:
              type: integer
              example: 1
            start_time:
              type: string
              format: date-time
              example: "2025-10-30T14:00:00-04:00"
    responses:
      200:
        description: Payment created successfully
        schema:
          type: object
          properties:
            client_secret:
              type: string
              example: "pi_3Nm8ExampleSecretKey"
        400:
          description: Error creating payment intent
          schema:
            type: object
            properties:
              error:
              type: string
              example: "Invalid email address"
    """ 


    data = request.get_json()
    amount = data.get("amount")
    currency = data.get("currency", "usd")

    client_email = data.get("client_email")
    full_name = data.get("full_name")
    phone_number = data.get("phone_number")
    start_time = data.get("start_time")
  
    user_timezone = data.get("timezone", "Africa/Douala")

    service_id = data.get("service_id")
    slot_id = data.get("slot_id")

    # validation
    if not re.match(r'[^@]+@[^@]+\.[^@]+', client_email):
        return {"message": "Invalid email address!"}
    elif not re.match(r'[A-Za-z]+', full_name):
        return {"message": "Username must contain only characters!"}
    elif not full_name:
        return {"message": "Please enter your first name!"}
    elif not client_email:
        return {"message": "Please enter your email!"}
    

    start_local = datetime.fromisoformat(start_time)

        # If naive datetimes, localize them
    if start_local.tzinfo is None:
        tz = pytz.timezone(user_timezone)
        start_local = tz.localize(start_local)

    # --- Convert to UTC ---
    start_utc = start_local.astimezone(pytz.UTC)

    metadata={
        "client_email": client_email,
        "first_name": full_name,
        "phone_number": phone_number,
        "service_id": service_id,
        "slot_id": slot_id,
        "start_time": start_utc
    }
    
    try:
        
        return PaymentService.create_payment(amount, currency, metadata)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
