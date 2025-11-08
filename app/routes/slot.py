from flask import Blueprint, request, jsonify
from app.services.slot_service import SlotService
from datetime import datetime
from app import db
import pytz


slot_bp = Blueprint("slot_bp", __name__)


@slot_bp.route("/delete_slot/<int:slot_id>", methods=["DELETE"])
def delete_slot(slot_id):
    try:
        SlotService.delete_slot(slot_id)
        return {"message": "slot deleted"}
    except Exception as e:
        return jsonify({"error": str(e)}), 400




@slot_bp.route("/create_slot/<int:user_id>", methods=["POST"])
def create_slot(user_id):
    """
    Create a slot (either date or period)
    """

    data = request.get_json()

    try:
        # --- Extract from body ---
        start_str = data.get("start")          # e.g. "2025-10-22T14:00:00-04:00"
        end_str = data.get("end")
        date = data.get("date")                # for date slot
        start_date = data.get("start_date")    # for period slot
        end_date = data.get("end_date")        # for period slot
        user_timezone = data.get("timezone", "Africa/Douala")

        # --- Parse times ---
        if not start_str or not end_str:
            return jsonify({"error": "Missing 'start' or 'end' time"}), 400

        start_local = datetime.fromisoformat(start_str)
        end_local = datetime.fromisoformat(end_str)

        # If naive datetimes, localize them
        if start_local.tzinfo is None:
            tz = pytz.timezone(user_timezone)
            start_local = tz.localize(start_local)
            end_local = tz.localize(end_local)

        # --- Convert to UTC ---
        start_utc = start_local.astimezone(pytz.UTC)
        end_utc = end_local.astimezone(pytz.UTC)

        if end_utc <= start_utc:
            return jsonify({"error": "End time must be after start time"}), 400

        # --- Create slot ---
        slot = SlotService.create_slot(
            start_utc,
            end_utc,
            user_id,
            user_timezone,
            date,
            start_date,
            end_date
        )

        # --- Return response ---
        return jsonify({
            "message": "Slot created successfully",
            "slot": slot
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400






@slot_bp.route("/get_slot/<int:service_id>", methods=["GET"])
def get_available_slots(service_id):
    """
    Retrieve available slots that are long enough for the selected service.
    """
    try:
        from app.models.repositories.service_repo import ServiceRepository

        # 1. Get the service duration
        service = ServiceRepository.get_service_by_id(service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 404

        service_duration = service.duration  # in minutes

        # 2. Fetch slots and filter
        slots = SlotService.get_available_slots(service_duration)
        return jsonify([s.to_dict() for s in slots]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400