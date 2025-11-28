import pytz
from app.models.repositories.appointment_repo import AppointmentRepository
from app.models.entities.appointment import appointmentEntity
from app.models.repositories.service_repo import ServiceRepository
from app.services.slot_service import SlotService
from app.services.payment_service import PaymentService
from app.services.calendar_service import CalendarService
from app.models.repositories.payment_repo import PaymentRepository
from app.integrations.google_calendar import cancel_google_event
from app.models.repositories.slot_repo import SlotRepository
from app.models.repositories.user_repo import UserRepository
from app.services.user_service import UserService
from datetime import datetime, timedelta, timezone

import secrets
from app.models.entities.appointment_token import tokenEntity
from app.models.repositories.token_repo import TokenRepository
from app.utils.email_util import EmailService



class AppointmentService:

    @staticmethod
    def book_appointment(client_email, full_name, phone_number, service_id, slot_id, stripe_id, client_start_time=None):
        try:
            # the stripe_id comes from the stripe_webhook
            payment = PaymentRepository.get_payment_by_stripe_id(stripe_id)

            # get service information
            service = ServiceRepository.get_service_by_id(service_id)
    
            # get the start_time and end_time from the slot table through the slot_id
            original_slot = SlotRepository.get_slot_by_id(slot_id)

            # check timezone info
            if original_slot.start_time.tzinfo is None:
                original_slot.start_time = original_slot.start_time.replace(tzinfo= timezone.utc)
            if original_slot.end_time.tzinfo is None:
                original_slot.end_time = original_slot.end_time.replace(tzinfo= timezone.utc)


            # performing the slot splitting here, if necessary
            slot_duration = (original_slot.end_time - original_slot.start_time).total_seconds() / 60
            if slot_duration > service.duration:

                 # Edit the next 6 lines
                if client_start_time is None:
                    print("Error: client_start_time is None")
                    
                    raise ValueError("Missing or invalid start time for ")

                # inside book_appointment()
                if isinstance(client_start_time, str):
                    client_start_time = datetime.fromisoformat(client_start_time)

                if client_start_time.tzinfo is None:
                    client_start_time = pytz.UTC.localize(client_start_time)
                
                # get the service end time
                service_end = client_start_time + timedelta(minutes=service.duration)

                SlotService.book_partial_slot(slot_id=slot_id, 
                                              slot_start_time=original_slot.start_time,
                                              slot_end_time=original_slot.end_time,
                                              slot_stylist_id=original_slot.stylist_id,
                                              slot_date=original_slot.date,
                                              service_start=client_start_time,
                                              service_end=service_end
                                            )
            else:
                # change slot status to booked
                SlotRepository.update_slot(slot_id, status="booked")

            # get the start_time and end_time from the slot table through the slot_id again, just incase the slot was updated
            slot = SlotRepository.get_slot_by_id(slot_id)


            # get stylist information
            stylist = UserRepository.get_users_by_id(slot.stylist_id)

    
            #   create an event on google calendar and return the id
            event = CalendarService.create_calendar_event(start_time = slot.start_time, 
                                                      end_time = slot.end_time, 
                                                      service_name = service.name, 
                                                      stylist_full_name = stylist.full_name,
                                                      user_email = client_email)
            
            #save user info
            client = UserService.create_user(full_name, client_email, phone_number, password=None)
            
            # save appointment to the database
            appointment = appointmentEntity(
                client_id = client.id,
                service_id = service_id,
                slot_id = slot_id,
                payment_id = payment.id, 
                google_event_id = event
            )
            # save appointment
            saved_appointment = AppointmentRepository.save_appointment(appointment)

       
            #### Generate a secure token ###
            token_value = secrets.token_urlsafe(32)
            # the token expiration date and time is the appointment slot start_time
            expire_at = slot.start_time

            new_token = tokenEntity( 
                appointment_id = saved_appointment.id,
                token = token_value,
                expires_at = expire_at
            )
            # save the new_token to the appointment_tokens table
            TokenRepository.save_token(new_token)

            # Now the confirmation/modification link generation
            manage_link = f"https://yourfrontend.com/appointments/{saved_appointment.id}/manage?token={token_value}" 


            # Send notification via email
            EmailService.send_appointment_confirmation(client_email, full_name, service.name, stylist.full_name, slot.date, manage_link)
         
            

            return saved_appointment.to_dict()
        
        except Exception as e:
            print("❌ Error in book_appointment():", str(e))
            import traceback
            traceback.print_exc()
            raise e


    @staticmethod
    def get_all_appointments():
        """ This function returns the appointment with its details in words, like the client name and others.
            It can also return a specific appointment, if the appointment id is given. 
        """
        return AppointmentRepository.get_all_appointments()


    @staticmethod
    def expire_old_appointments():
        """
        Marks all appointments whose slot end_time < current time as completed, then setting the slot as expired .
        This logic is reusable — it can be triggered by APScheduler, cron, or an API.
        """
        count = AppointmentRepository.expire_old_appointments()

    
        return {f"Marked {count} appointments as completed"}



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
        
        # get user info inorder to get their email
        user = UserRepository.get_users_by_id(appointment.client_id)

        # get service information
        service = ServiceRepository.get_service_by_id(service_id)

        # get stylist information
        stylist = UserRepository.get_users_by_id(slot.stylist_id)

        # Create new calendar event
        new_event_id = CalendarService.create_calendar_event(slot.start_time, slot.end_time, service.name, stylist.full_name, user.email)

        # changing the status of the slots (if a new slot is selected)
        if slot_id:
            # free up the former slot occupied, if a new slot is selected
            SlotRepository.update_slot(appointment.slot_id, status="available")

            # setting the status of the new selected slot to booked
            SlotRepository.update_slot(slot_id, status="booked")

        # Update appointment in DB with new details
        updated_appointment = AppointmentRepository.update_appointment(
            appointment_id, service_id, slot_id, google_event_id=new_event_id
        )
       
        return {"message": "Appointment updated successfully"}



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

        # delete the token associated to the cancelled appointment
        TokenRepository.delete_token(appointment.id)

        # change slot status to available
        SlotRepository.update_slot(appointment.slot_id, status="available")

        return {"message": "Appointment cancelled successfully"}  
      