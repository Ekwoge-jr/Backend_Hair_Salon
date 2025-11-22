import pytz
from app.models.entities.slot import slotEntity
from app.models.repositories.slot_repo import SlotRepository
from datetime import datetime, timedelta, timezone
from flask import jsonify


class SlotService:

    msg=''
    @staticmethod
    def create_slot(start_time, end_time, stylist_id, user_timezone, date=None, start_date=None, end_date=None):

        if start_time == None:
            msg = "Please indicate start time"
            return msg
        elif end_time == None:
            msg = "Please indicate end time"
            return msg
        if date is not None:
            date = date

        # Extract only the time part from start_time and end_time
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)

        # if a range is given, create one slot per day
        slots_created = []
        if start_date and end_date:
            current_date = datetime.fromisoformat(start_date).date()
            end_range = datetime.fromisoformat(end_date).date()
            
            while current_date <= end_range:

                # Replace the date part but keep the time and tzinfo
                new_start = start_time.replace(year=current_date.year, month=current_date.month, day=current_date.day)
                new_end = end_time.replace(year=current_date.year, month=current_date.month, day=current_date.day)

                slot = slotEntity(
                    start_time = new_start,
                    end_time = new_end,
                    date = current_date,
                    stylist_id = stylist_id
                )
                SlotRepository.save_slot(slot) 
                slots_created.append(slot.to_dict(user_timezone))
                current_date += timedelta(days=1)
        
        else:
            # single-day slot   
            slot = slotEntity(
                start_time = start_time,
                end_time = end_time,
                date = date,
                stylist_id = stylist_id
            )
            SlotRepository.save_slot(slot)
            slots_created.append(slot.to_dict(user_timezone))

        return slots_created


    @staticmethod
    def expire_old_slots():
        """
        Marks all slots whose end_time < current time as expired.
        This logic is reusable — it can be triggered by APScheduler, cron, or an API.
        """
        count = SlotRepository.expire_old_slots()
        return {f"Marked {count} as expired"}


    @staticmethod
    def get_all_available_slots():
        return SlotRepository.get_slot_by_status("available")    
    
    @staticmethod
    def get_slots_by_date(date):
        return SlotRepository.get_slot_by_date(date)

    @staticmethod
    def get_all_slots():
        return SlotRepository.get_all_slots() 
    
    @staticmethod
    def delete_slot(slot_id):
        return SlotRepository.delete_slot(slot_id)





    @staticmethod
    def get_available_slots(min_duration=None):
        slots = SlotRepository.get_slot_by_status(status="available")

        if not min_duration:
            return slots

        # Filter based on duration
        valid_slots = []
        for slot in slots:

            # check timezone info
            if slot.start_time.tzinfo is None:
                slot.start_time = slot.start_time.replace(tzinfo= timezone.utc)
            if slot.end_time.tzinfo is None:
                slot.end_time = slot.end_time.replace(tzinfo= timezone.utc)

            slot_duration = (slot.end_time - slot.start_time).total_seconds() / 60
            if slot_duration >= min_duration:
                valid_slots.append(slot)
        
        return valid_slots
    



    # function to split one slot, to support multiple appointment for a particular slot
    @staticmethod
    def book_partial_slot(slot_id, slot_start_time, slot_end_time, slot_stylist_id, slot_date, service_start, service_end):

        # Convert input times
        if isinstance(service_start, str):
            service_start = datetime.fromisoformat(service_start)
        if isinstance(service_end, str):
            service_end = datetime.fromisoformat(service_end)

        # Case 1: Before part
        if service_start > slot_start_time:
            before_slot = slotEntity(
                start_time=slot_start_time,
                end_time=service_start,
                date=slot_date,
                stylist_id=slot_stylist_id,
                # status="available"
            )
            SlotRepository.save_slot(before_slot)

        # Case 2: After part
        if service_end < slot_end_time:
            after_slot = slotEntity(
                start_time=service_end,
                end_time=slot_end_time,
                date=slot_date,
                stylist_id=slot_stylist_id,
                # status="available"
            )
            SlotRepository.save_slot(after_slot)

        # Update booked slot portion
        SlotRepository.update_slot(slot_id, start_time=service_start, end_time=service_end, status="booked")

        return {"message": "Slot booked and split successfully"}
