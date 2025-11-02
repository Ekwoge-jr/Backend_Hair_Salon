from app.models.repositories.appointment_repo import AppointmentRepository
from app.models.entities.appointment import appointmentEntity
from app.services.payment_service import PaymentService
from app.services.calendar_service import CalendarService
from app.models.repositories.payment_repo import PaymentRepository
from app.integrations.google_calendar import cancel_google_event
from app.models.repositories.slot_repo import SlotRepository
import datetime
import secrets

from app.models.repositories.slot_repo import SlotRepository


class AppointmentService:

    @staticmethod
    def book_appointment(client_id, service_id, slot_id, stripe_id):
        
        # the stripe_id comes from the stripe_webhook
        payment = PaymentRepository.get_payment_by_stripe_id(stripe_id)
    
        # get the start_time and end_time from the slot table through the slot_id
        slot = SlotRepository.get_slot_by_id(slot_id)
    
        # create an event on google calendar and return the id
        event = CalendarService.create_calendar_event(start_time = slot.start_time, 
                                                      end_time = slot.end_time, 
                                                      service_id = service_id, 
                                                      stylist_id = slot.stylist_id)

        # save appointment to the database
        appointment = appointmentEntity(
            client_id = client_id,
            service_id = service_id,
            slot_id = slot_id,
            payment_id = payment.id, 
            google_event_id = event
        )
        # save appointment
        saved_appointment = AppointmentRepository.save_appointment(appointment)

        # change slot status to booked
        SlotRepository.update_slot_status(slot_id, "booked")

       



        return saved_appointment.to_dict()



# update
    @staticmethod
    def update_appointment(appointment_id, service_id = None, slot_id = None):
        """
        Updates an appointment and syncs it with Google Calendar.
        """
        appointment = AppointmentRepository.get_appointment_by_id(appointment_id)
        if not appointment:
            return False
        
        # Cancel old calendar event if it exists
        if appointment.google_event_id:
            cancel_result = cancel_google_event(appointment.google_event_id)
            if "error" in cancel_result:
                return {"error": f"Failed to cancel old Google event: {cancel_result['error']}"}

        # Get the new slot
        slot = SlotRepository.get_slot_by_id(slot_id)
        if not slot:
            return {"error": "Slot not found"}

        # Create new calendar event
        new_event_id = CalendarService.create_calendar_event(slot.start_time, slot.end_time, service_id, slot.stylist_id)

        # changing the status of the slots (if a new slot is selected)
        if slot_id:
            # free up the former slot occupied, if a new slot is selected
            SlotRepository.update_slot_status(appointment.slot_id, "available")

            # setting the status of the new selected slot to booked
            SlotRepository.update_slot_status(slot_id, "booked")

        # Update appointment in DB with new details
        updated_appointment = AppointmentRepository.update_appointment(
            appointment_id, service_id, slot_id, google_event_id=new_event_id
        )

        return updated_appointment.to_dict()



# cancle
    @staticmethod
    def cancle_appointment(appointment_id):
        appointment = AppointmentRepository.get_appointment_by_id(appointment_id)

        if not appointment:
            return {"error": "Appointment not found for this Google event"}

        event_result = cancel_google_event(appointment.google_event_id)

        if "error" in event_result:
            return {"error": f"Failed to cancel Google event: {event_result['error']}"}
    
        # get the appointment using the google_event_id
        # appointment = AppointmentRepository.get_appointment_by_event_id(event_id)
        

            # update the appointment status to cancelled
        AppointmentRepository.update_status(appointment.id, "cancelled")

        # change slot status to available
        SlotRepository.update_slot_status(appointment.slot_id, "available")

        return {"message": "Appointment cancelled successfully"}  
      


