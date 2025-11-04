from flask import Blueprint, request, jsonify
from app import db
from app.models.repositories.service_repo import ServiceRepository
from app.models.entities.service import serviceEntity
from app.services.user_service import UserService
from app.models.entities.user import userEntity
from app.services.service_service import ServiceService
from app.services.appointment_service import AppointmentService

from datetime import datetime

import pytz
from app.services.slot_service import SlotService




user_bp = Blueprint("user_bp", __name__)



@user_bp.route("/create-service", methods= ["POST"])
def create_service():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    duration = data.get("duration")
    
    
    try:
        result=  ServiceService.create_service(name, description, price, duration)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@user_bp.route("/create-user", methods= ["POST"])
def create_user():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    address = data.get("address")
    password = data.get("password")
    
    
    try:
        result=  UserService.create_user(first_name, last_name, email, phone_number, address, password)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/get", methods=["GET"])
def select():
    try:
        results = UserService.get_all_users()
        return jsonify([r.to_dict() for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@user_bp.route("/update/<int:user_id>", methods=["POST"])
def update(user_id):
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    address = data.get("address")
    password = data.get("password")
    try:
        results = UserService.update_user(user_id,first_name,last_name,email,phone_number,address,password)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route("/update_role/<int:user_id>", methods=["POST"])
def status(user_id):
    return UserService.update_user(user_id, role="stylist")

@user_bp.route("/create_slot/<int:user_id>", methods=["POST"])
def slot(user_id):
    data = request.get_json()
    
    try:
         # --- Extract data from request ---
        start_str = data.get("start")      # e.g. "2025-10-22T14:00:00-04:00"
        end_str = data.get("end")          # e.g. "2025-10-22T15:00:00-04:00"
        user_timezone = data.get("timezone", "Africa/Douala")  # default fallback

        if not start_str or not end_str:
            return jsonify({"error": "Missing start or end time"}), 400

        # --- Parse the input times ---
        start_local = datetime.fromisoformat(start_str)
        end_local = datetime.fromisoformat(end_str)

        # If datetimes are *naive* (no timezone info), assume user_timezone
        if start_local.tzinfo is None:
            local_tz = pytz.timezone(user_timezone)
            start_local = local_tz.localize(start_local)
            end_local = local_tz.localize(end_local)

        # --- Convert to UTC for consistent storage ---
        start_utc = start_local.astimezone(pytz.UTC)
        end_utc = end_local.astimezone(pytz.UTC)

        # --- Extract just the date (in user's local time) ---
        date = start_local.date()

        # Pass UTC times to service layer
        slot = SlotService.create_slot(start_utc, end_utc, date, user_id)
        print(slot.to_dict())

        # slot = SlotService.create_slot(start_time, end_time, date, user_id)
        return jsonify({
            "message": "Slot created successfully",
            "slot": slot.to_dict() if hasattr(slot, "to_dict") else str(slot)

        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@user_bp.route("/update_appointment/<int:appointment_id>", methods=["PUT"])
def appointment(appointment_id):
    data = request.get_json()
    service = data.get("service_id")
    slot = data.get("slot_id")
    return AppointmentService.update_appointment(appointment_id, service, slot)





############ 
@user_bp.route("/appointments/<int:id>/manage")
def manage_appointment(id):
    token = request.args.get("token")
    data = verify_token(token)
    
    
    # Show appointment info or allow updates
    appointment = AppointmentRepository.get_appointment_by_id(id)
    return render_template("manage_appointment.html", appointment=appointment)
