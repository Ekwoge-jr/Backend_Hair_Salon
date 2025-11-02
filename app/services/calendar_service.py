from app.integrations.google_calendar import create_google_event
from app.models.repositories.service_repo import ServiceRepository
from app.models.repositories.user_repo import UserRepository
from app.models.repositories.appointment_repo import AppointmentRepository
import datetime

class CalendarService:

    @staticmethod
    def create_calendar_event(start_time, end_time, service_id, stylist_id):

        # get service name for the event description
        service = ServiceRepository.get_service_by_id(service_id)

        # get the stylist name for the event description
        stylist = UserRepository.get_users_by_id(stylist_id)


        # create the event on google_calendar and get the event id
        event_id = create_google_event(
            summary = f"{service.name} Appointment",
            description = f"Client wants to do {service.name} and is to be done by {stylist.first_name}",
            start_time = start_time.isoformat() + "Z",
            end_time = end_time.isoformat() + "Z",
        )

        return event_id
    