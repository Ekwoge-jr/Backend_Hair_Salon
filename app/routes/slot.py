from flask import Blueprint, request, jsonify
from app.services.slot_service import SlotService
from datetime import datetime
from app import db
import pytz


slot_bp = Blueprint("slot_bp", __name__)


@slot_bp.route("/create_slot/<int:user_id>", methods=["POST"])
def create_slot(user_id):

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
    

@slot_bp.route("/delete_slot/<int:slot_id>", methods=["DELETE"])
def delete_slot(slot_id):
    try:
        SlotService.delete_slot(slot_id)
        return {"message": "slot deleted"}
    except Exception as e:
        return jsonify({"error": str(e)}), 400
