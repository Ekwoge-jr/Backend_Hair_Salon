from sqlalchemy.orm import Session
from app import db
from app.models.entities.appointment_token import tokenEntity
from app.models.orm.appointment_token_model import AppointmentTokenModel

class TokenRepository:

    # conversion
    @staticmethod
    def _to_entity(model: AppointmentTokenModel):
        """Convert ORM model to Entity."""
        return tokenEntity(
            id = model.id,
            appointment_id = model.appointment_id,
            token = model.token,
            expires_at = model.expires_at
        )
    

    # create
    @staticmethod
    def save_token(entity: tokenEntity):
        new_token = AppointmentTokenModel(
            appointment_id = entity.appointment_id,
            token = entity.token,
            expires_at = entity.expires_at
        )
        db.session.add(new_token)
        db.session.commit()
        db.session.refresh(new_token)

        # Return the entity with ID set
        entity.id = new_token.id
        return entity
    

    
    

    # delete
    @staticmethod
    def delete_token(appointment_id):
        token = db.session.query(AppointmentTokenModel).filter_by(appointment_id=appointment_id).first()
        if token:
            db.session.delete(token)
            db.session.commit()
            return True
        return False