from app.models.repositories.appointment_repo import AppointmentRepository
from app.models.entities.appointment import appointmentEntity
from app.integrations.stripe import create_payment_intent
from app.integrations.google_calendar import create_google_event


class AppointmentService:

    @staticmethod
    def book_appointment(amount, client_id, service_id, slot_id, payment_id, google_event_id):
        
        appointment = appointmentEntity(
            client_id = client_id,
            service_id = service_id,
            slot_id = slot_id,
            payment_id = payment_id,
            google_event_id = google_event_id
        )
        return AppointmentRepository.save_appointment(appointment)
        