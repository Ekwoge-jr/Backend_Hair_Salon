from app.models.entities.slot import slotEntity
from app.models.repositories.slot_repo import SlotRepository
from flask import jsonify


class SlotService:

    msg=''
    @staticmethod
    def create_slot(start_time, end_time, date, stylist_id):

        if start_time == None:
            msg = "Please indicate start time"
            return msg
        elif end_time == None:
            msg = "Please indicate end time"
            return msg
        elif date == None:
            msg = "Please indicate date"
            return msg
        else:    
            slot = slotEntity(
                start_time = start_time,
                end_time = end_time,
                date = date,
                stylist_id = stylist_id
            )
            return SlotRepository.save_slot(slot)    


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
    def change_status(slot_id, status):
        return SlotRepository.update_slot_status(slot_id, status)
    

    @staticmethod
    def delete_slot(slot_id):
        return SlotRepository.delete_slot(slot_id)