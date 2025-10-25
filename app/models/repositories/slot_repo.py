from app.models.orm.slot_model import SlotModel
from sqlalchemy.orm import Session
from app import db
from app.models.entities.slot import slotEntity

class SlotRepository:

# conversion
    @staticmethod
    def _to_entity(model: SlotModel):
        """Convert ORM model to Entity."""
        return slotEntity(
            id=model.id,
            start_time = model.start_time,
            end_time = model.end_time,
            date = model.date,
            stylist_id = model.stylist_id,
            status = model.status
        )
    


# create
    @staticmethod
    def save_slot(entity: slotEntity):
        new_slot = SlotModel(
            start_time = entity.start_time,
            end_time = entity.end_time,
            date = entity.date,
            stylist_id = entity.stylist_id
        )
        db.session.add(new_slot)
        db.session.commit()
        db.session.refresh(new_slot)

        # Return the entity with ID set
        entity.id = new_slot.id
        return entity


# read
    @staticmethod
    def get_all_slots():
        results = db.session.query(SlotModel).all()
        return [SlotRepository._to_entity(slot) for slot in results]
    
    @staticmethod
    def get_slot_by_id(slot_id: int):
        result = db.session.query(SlotModel).filter(SlotModel.id == slot_id).first()
        return SlotRepository._to_entity(result) if result else None
    
    @staticmethod
    def get_slot_by_date(date):
        results = db.session.query(SlotModel).filter(SlotModel.date == date).all()
        return [SlotRepository._to_entity(slot) for slot in results]
    
    @staticmethod
    def get_slot_by_status(status):
        results = db.session.query(SlotModel).filter(SlotModel.status == status).all()
        return [SlotRepository._to_entity(slot) for slot in results]
    

# update
    @staticmethod
    def update_slot_status(slot_id, status):
        slot = db.session.query(SlotModel).filter_by(id=slot_id).first()
        if slot:
            slot.status = status
            db.session.commit()
            db.session.refresh(slot)
            return SlotRepository._to_entity(slot)
        return None
    

# delete
    @staticmethod
    def delete_slot(slot_id):
        slot = db.session.query(SlotModel).filter_by(id=slot_id).first()
        if slot:
            db.session.delete(slot)
            db.session.commit()
            return True
        return False