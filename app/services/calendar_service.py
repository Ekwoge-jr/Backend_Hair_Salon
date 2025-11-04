from app.integrations.google_calendar import create_google_event
from app.models.repositories.service_repo import ServiceRepository
from app.models.repositories.user_repo import UserRepository
from app.models.repositories.appointment_repo import AppointmentRepository
import datetime

class CalendarService:

    @staticmethod
    def create_calendar_event(start_time, end_time, service_name, stylist_first_name):

        # create the event on google_calendar and get the event id
        event_id = create_google_event(
            summary = f"{service_name} Appointment",
            description = f"Your have a {service_name} appointment which is to be done by {stylist_first_name}",
            start_time = start_time.isoformat() + "Z",
            end_time = end_time.isoformat() + "Z",
        )

        return event_id
    