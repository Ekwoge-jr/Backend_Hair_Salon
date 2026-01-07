from flask import Blueprint, request, jsonify
from app.services.slot_service import SlotService
from datetime import datetime
from app import db
import pytz

import json

from flask_jwt_extended import jwt_required, get_jwt_identity


slot_bp = Blueprint("slot_bp", __name__)


@slot_bp.route("/delete_slot/<int:user_id>/<int:slot_id>", methods=["DELETE"])
@jwt_required()
def delete_slot(user_id,slot_id):
    
    """
    Delete a slot
    ---
    tags:
      - Slots
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the stylist
      - name: slot_id
        in: path
        type: integer
        required: true
        description: ID of the slot to delete
    responses:
      200:
        description: Slot deleted successfully
      400:
        description: Error deleting slot
    """

    # current_user = get_jwt_identity()
    print("In the delete function")
    
    # ensure only stylists can create slots
    # if current_user["id"] != user_id or current_user["role"] != "stylist":
    #     return jsonify({"error": "Unauthorized"}), 403
    identity_data = get_jwt_identity()
    if isinstance(identity_data, str):
        try:
            user_dict = json.loads(identity_data)
            token_id = int(user_dict.get("id"))
            token_role = user_dict.get("role")
        except:
            token_id = int(identity_data)
            token_role = "stylist" # Fallback
    else:
        token_id = int(identity_data.get("id"))
        token_role = identity_data.get("role")

    # 2. AUTHORIZATION CHECK
    # Note: For slots, we allow the specific stylist OR an admin
    if token_id != user_id and token_role != "stylist":
        return jsonify({"error": "Unauthorized"}), 403


    try:
        SlotService.delete_slot(slot_id)
        return {"message": "slot deleted"}
    except Exception as e:
        return jsonify({"error": str(e)}), 400




@slot_bp.route("/create_slot/<int:user_id>", methods=["POST"])
@jwt_required()
def create_slot(user_id):
    """
    Create a slot (either date or period)
    ---
    tags:
      - Slots
    description: Creates a new slot with start time, end time, date and can also take a range of dates (start date and end date).
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the stylist creating the slot
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            start:
              type: string
              format: date-time
              example: "2025-11-22T14:00:00-04:00"
            end:
              type: string
              format: date-time
              example: "2025-11-22T17:00:00-04:00"
            date:
              type: string
              format: date
              example: "2025-11-22"
            start_date:
              type: string
              format: date
              example: "2025-11-22"
            end_date:
              type: string
              format: date 
              example: "2025-11-30"
    responses:
      200:
        description: User created successfully.
      400:
        description: Invalid input or user creation failed.
    """

    identity_data = get_jwt_identity()
    
    # ensure only stylists can create slots
    # if current_user["id"] != user_id or current_user["role"] != "stylist":
    #     return jsonify({"error": "Unauthorized"}), 403
    if isinstance(identity_data, str):
        try:
            user_dict = json.loads(identity_data)
            token_id = int(user_dict.get("id"))
            token_role = user_dict.get("role")
        except:
            token_id = int(identity_data)
            token_role = "stylist" # Fallback
    else:
        token_id = int(identity_data.get("id"))
        token_role = identity_data.get("role")

    # 2. AUTHORIZATION CHECK
    # Note: For slots, we allow the specific stylist OR an admin
    if token_id != user_id and token_role != "stylist":
        return jsonify({"error": "Unauthorized"}), 403
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
    Retrieve available slots
    ---
    tags: 
      - Slots
    description: Fetches a list of all available slots that can contain a particuler service from the database.
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        
    responses:
      200:
        description: List of slots retrieved successfully.
        content: 
          application/json: 
            schema:
              type: array
              items:
                type: object
              properties:
                id: 
                  type: integer
                  example: 1
                start_time: 
                  type: string
                end_time: 
                  type: string
                date: 
                  type: string
                stylist_id:
                  type: integer
      400: 
        description: Error retrieving slots.
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
    


    
@slot_bp.route("/get_stylist_slots/<int:stylist_id>", methods=["GET"])
def get_slots_by_stylist(stylist_id):
    
    """
    Retrieve all slots for a particular stylist
    ---
    tags: 
      - Slots
    description: Fetches a list of all slots that were created by a particular stylist from the database.
    parameters:
      - name: stylist_id
        in: path
        type: integer
        required: true
        
    responses:
      200:
        description: List of slots retrieved successfully.
        content: 
          application/json: 
            schema:
              type: array
              items:
                type: object
              properties:
                id: 
                  type: integer
                  example: 1
                start_time: 
                  type: string
                end_time: 
                  type: string
                date: 
                  type: string
                stylist_id:
                  type: integer
      400: 
        description: Error retrieving slots.
    """
    try:
        slots = SlotService.get_slots_by_stylist(stylist_id)
        return jsonify([s.to_dict() for s in slots]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@slot_bp.route("/update_slot/<int:stylist_id>/<int:slot_id>", methods=["GET"])
def update_slot(stylist_id, slot_id):
    
    """
    Update a slot
    ---
    tags:
      - Slots
    description: Updates an existing slot.
    consumes:
      - multipart/form-data
    parameters:
      - name: stylist_id
        in: path
        type: integer
        required: true
        description: ID of the stylist
      - name: slot_id
        in: path
        type: integer
        required: true
        description: ID of the slot to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            start_time:
              type: string
              format: date-time
              example: "2025-11-22T14:00:00-04:00"
            end_time:
              type: string
              format: date-time
              example: "2025-11-22T17:00:00-04:00"
            date:
              type: string
              format: date
              example: "2025-11-22"  
    responses:
      200:
        description: Slot updated successfully
      400:
        description: Error updating slot
    """

    data = request.get_json()

    try:
      # --- Extract from body ---
      start_str = data.get("start")          # e.g. "2025-10-22T14:00:00-04:00"
      end_str = data.get("end")
      date = data.get("date")                # for date slot
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
      slot = SlotService.update_slot(
          slot_id,
          start_utc,
          end_utc,
          date
      )
      

      # --- Return response ---
      return jsonify({
          "message": "Slot Updated successfully",
          "slot": slot
      }), 201
    except Exception as e:
      return jsonify({"error": str(e)}), 400
