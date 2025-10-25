from flask import Blueprint, jsonify
from app.integrations.google_calendar import create_google_event
from app.models.orm.appointment_model import AppointmentModel
from app import db
import datetime

calendar_bp = Blueprint("calendar_bp", __name__)

@calendar_bp.route("/create-event")
def test_event():
    start = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat() + "Z"
    end = (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat() + "Z"
    

    event_id = create_google_event(
        summary="Hair Appointment",
        description="Client hair session with stylist",
        start_time=start,
        end_time=end,
    )

    save = AppointmentModel(
        client_id = 12,
        service_id = 12,
        slot_id = 2,
        payment_id = 1,
        google_event_id = event_id
    )
    db.session.add(save)
    db.session.commit()

    return jsonify({"message": "Event created successfully", "event_id": event_id})
