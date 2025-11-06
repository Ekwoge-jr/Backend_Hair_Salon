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




@user_bp.route("/update_role/<int:user_id>", methods=["POST"])
def status(user_id):
    return UserService.update_user(user_id, role="stylist")






