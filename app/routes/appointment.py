from flask import Blueprint, request, jsonify
from app.models.repositories.token_repo import TokenRepository
from app.services.appointment_service import AppointmentService
from datetime import datetime, timezone
from app import db
from flasgger import swag_from

appointment_bp = Blueprint("appointment_bp", __name__)

# get an appointment from the link sent to the client's email
@appointment_bp.route("/<int:appointment_id>/manage")


def manage_appointment(appointment_id):

    """
    Manage an appointment via email link
    ---
    tags:
      - Appointments
    description: Retrieves appointment details using the secure link sent to the client’s email. The link requires a valid token.
    parameters:
      - in: path
        name: appointment_id
        type: integer
        required: true
        description: Unique appointment ID
      - in: query
        name: token
        type: string
        required: true,
        description: Secure token provided in the email link
    responses:
      200:
        description: Appointment details successfully retrieved
        schema:
          type: object
          properties:
            appointment_id: 
              type: integer
            service_name: 
              type: string
            slot: 
              type: string
            status: 
              type: string
      400:
        description: Missing token
      403:
        description: Invalid or expired token
    """


    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400
    # search for the token
    record = TokenRepository.get_token(appointment_id, token)

    if not record:
        return jsonify({"error": "Invalid token or link has expired"}), 403
    
    # ✅ Expiration check
    if datetime.now(timezone.utc) > record.expires_at:
        return jsonify({"error": "This link has expired"}), 403

    # ✅ Token is valid
    appointment = AppointmentService.get_all_appointments(appointment_id)

    return appointment


# edit
@appointment_bp.route("/update-payment/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):

    """
    Update an existing appointment
    ---
    tags:
      - Appointments
    description: Allows the client to modify an existing appointment by changing the service or slot.
    parameters:
      - in: path
        name: appointment_id
        type: integer
        required: true
        description: Unique appointment ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            service_id: 
              type: integer
              example: 1
            slot_id: 
              type: integer
              example: 5
    responses:
      200:
        description: Appointment updated successfully
      400:
        description: Invalid input or missing data
      404:
        description: Appointment not found
    """

    data = request.get_json()

    service_id = data.get("service_id")
    slot_id = data.get("slot_id")

    return AppointmentService.update_appointment(appointment_id, service_id, slot_id)


# cancel
@appointment_bp.route("/cancel-payment/<int:appointment_id>", methods=["DELETE"])
def cancel_appointment(appointment_id):

    """
    Cancel an appointment
    ---
    tags:
      - Appointments
    description: Cancels a booked appointment and frees up the associated slot.
    parameters:
      - in: path
        name: appointment_id
        type: integer
        required: true
        description: Unique appointment ID
    responses:
      200:
        description: Appointment cancelled successfully
      400:
        description: Invalid appointment ID
      404:
        description: Appointment not found
    """
    
    return AppointmentService.cancle_appointment(appointment_id)