from datetime import timedelta, timezone, datetime
from app.models.repositories.payment_repo import PaymentRepository
from app.models.entities.payment import paymentEntity
from app.integrations.stripe import create_payment_intent
from app.models.repositories.service_repo import ServiceRepository
from app.models.repositories.slot_repo import SlotRepository

class PaymentService:

    @staticmethod
    def create_payment(amount, currency, metadata):
        # get service information
        service = ServiceRepository.get_service_by_id(metadata["service_id"])
    
        # get the start_time and end_time from the slot table through the slot_id
        slot = SlotRepository.get_slot_by_id(metadata["slot_id"])


        if slot.start_time.tzinfo is None:
            slot.start_time = slot.start_time.replace(tzinfo= timezone.utc)
        if slot.end_time.tzinfo is None:
            slot.end_time = slot.end_time.replace(tzinfo= timezone.utc)

        print("input tz:", (metadata["start_time"]).tzinfo)
        print("s start tz:", slot.start_time.tzinfo)
        print("s end tz:", slot.end_time.tzinfo)



        slot_duration = (slot.end_time - slot.start_time).total_seconds() / 60
        if slot_duration > service.duration and metadata["start_time"]==None:
            return ({"error": "Please input a start time"})
        

        # Check if the requested range fits in the slot
        # get the service end time
        service_end = metadata["start_time"] + timedelta(minutes=service.duration)

        print("start:", metadata["start_time"])
        print("s start:", slot.start_time )
        print("s end:", slot.end_time )
        
        if not (slot.start_time <= metadata["start_time"] and service_end <= slot.end_time):
            return {"error": "Service time does not fit within available slot"}, 400
        

        # make payment intent in stripe
        payment_intent = create_payment_intent(amount, currency, metadata)

    
        # save the payment to our database
        payment = paymentEntity(
        stripe_id = payment_intent["id"],
        amount = payment_intent["amount"] / 100,  # convert from cents
        currency = payment_intent["currency"],
        status = payment_intent["status"]
        )
        PaymentRepository.save_payment(payment)
        return payment_intent