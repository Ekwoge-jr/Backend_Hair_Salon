from app.models.orm.appointment_model import AppointmentModel
from app.models.entities.appointment import appointmentEntity
from sqlalchemy.orm import Session
from app import db
from sqlalchemy import text

class AppointmentRepository:
    

# conversion
    @staticmethod
    def _to_entity(model: AppointmentModel):
        """Convert ORM model to Entity."""
        return appointmentEntity(
            id = model.id,
            client_id = model.client_id,
            service_id = model.service_id,
            slot_id = model.slot_id,
            payment_id = model.payment_id,
            google_event_id = model.google_event_id,
            created_at = model.created_at,
            status = model.status
        )



# create
    @staticmethod
    def save_appointment(entity: appointmentEntity):
        new_appointment = AppointmentModel(
            client_id = entity.client_id,
            service_id = entity.service_id,
            slot_id = entity.slot_id,
            payment_id = entity.payment_id,
            google_event_id = entity.google_event_id
        )
        db.session.add(new_appointment)
        db.session.commit()
        db.session.refresh(new_appointment)

        # Return the entity with ID set
        entity.id = new_appointment.id
        return entity
    

# read
    @staticmethod
    def get_all_appointments():
        results = db.session.query(AppointmentModel).all()
        return [AppointmentRepository._to_entity(appointment) for appointment in results]
    
    @staticmethod
    def get_appointment_by_id(appointment_id):
        result = db.session.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
        return AppointmentRepository._to_entity(result) if result else None
    
    @staticmethod
    def get_appointments_by_client(client_id):
        results = db.session.query(AppointmentModel).filter(AppointmentModel.client_id == client_id).all()
        return [AppointmentRepository._to_entity(appointment) for appointment in results]

    @staticmethod
    def get_appointments_by_status(status):
        results = db.session.query(AppointmentModel).filter(AppointmentModel.status == status).all()
        return [AppointmentRepository._to_entity(appointment) for appointment in results]

    @staticmethod
    def get_appointments_by_slot_date(date):
        sql = text("""
            SELECT a*
            FROM appointments a
            INNERJOIN slots s ON a.slot_id = s.id
            WHERE s.date = :date
        """)
        result = db.session.execute(sql, {"date": date})
        appointments = result.fetchall()
        return [AppointmentRepository._to_entity(appointment) for appointment in appointments]
    

# update
    @staticmethod
    def update_status(appointment_id, status):
        appointment = db.session.query(AppointmentModel).filter_by(id=appointment_id).first()
        if appointment:
            appointment.status = status
            db.session.commit()
            db.session.refresh(appointment)
            return True
        return False
    

