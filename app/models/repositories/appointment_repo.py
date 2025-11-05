from app.models.orm.appointment_model import AppointmentModel
from app.models.entities.appointment import appointmentEntity
from sqlalchemy.orm import Session
from app import db
from sqlalchemy import text
from datetime import datetime, timezone
from app.models.orm.slot_model import SlotModel
from app.models.repositories.token_repo import TokenRepository

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
    def get_all_appointments(appointment_id = None):
        """ This function returns the appointment with its details in words, like the client name and others.
            It can also return a specific appointment, if the appointment id is given. 
        """
        sql = """
        SELECT 
            a.id AS appointment_id,
            a.status AS appointment_status,
            a.created_at AS appointment_created_at,
            a.google_event_id,
            u.first_name AS client_name,
            u.email AS client_email,
            se.name AS service_name,
            us.first_name AS stylist_name,
            s.start_time,
            s.end_time,
            s.date
        FROM appointments a
        INNER JOIN users u ON a.client_id = u.id
        INNER JOIN services se ON a.service_id = se.id
        INNER JOIN slots s ON a.slot_id = s.id
        INNER JOIN users us ON s.stylist_id = us.id
        """

        # Add this condition if appointment_id is provided
        if appointment_id:
            sql += " WHERE a.id = :appointment_id"

        sql += " ORDER BY s.date DESC"

        # Execute SQL
        params = {"appointment_id": appointment_id} if appointment_id else {}
        results = db.session.execute(text(sql), params).mappings().all()

        if not results:
            return None if appointment_id else []
        
        # results = db.session.execute(sql).mappings().all()
        if appointment_id:
            return dict(results[0])  # return one record as dict
        else:
            return [dict(row) for row in results]  # return all as list
       
    
    @staticmethod
    def get_appointment_by_id(appointment_id):
        result = db.session.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
        return AppointmentRepository._to_entity(result) if result else None
    
    @staticmethod
    def get_appointment_by_event_id(event_id):
        result = db.session.query(AppointmentModel).filter(AppointmentModel.google_event_id == event_id).first()
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
            SELECT a.*
            FROM appointments a
            INNER JOIN slots s ON a.slot_id = s.id
            WHERE s.date = :date
        """)
        result = db.session.execute(sql, {"date": date})
        appointments = result.fetchall()
        return [AppointmentRepository._to_entity(appointment) for appointment in appointments]
    
    @staticmethod
    def expire_old_appointments():
        now = datetime.now(timezone.utc)
        expired = 0
        try:    
            sql = text("""
                SELECT a.id AS a_id, a.status AS a_status, s.id AS s_id, s.end_time AS s_end_time
                FROM appointments a
                INNER JOIN slots s ON a.slot_id = s.id
                WHERE a.status = 'booked'
            """)
            results = db.session.execute(sql).mappings().all()

            for row in results:
                end_time = row["s_end_time"]
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone.utc)

                if end_time < now:
                #if row["s_end_time"] < now:
                    db.session.execute(
                        text("UPDATE appointments SET status = 'completed' WHERE id = :id"),
                        {"id": row["a_id"]}
                    )
                    TokenRepository.delete_token(row["a_id"])
                    db.session.execute(
                        text("UPDATE slots SET status = 'expired' WHERE id = :id"),
                        {"id": row["s_id"]}
                    )
                    expired += 1
        
            db.session.commit()
            return expired 

        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Failed to expire old appointments: {e}")
            return {"error": f"Failed to update appointment: {str(e)}"}


# update
    @staticmethod
    def update_appointment(appointment_id, service_id = None, slot_id = None, google_event_id = None):
        
        try:
            appointment = db.session.query(AppointmentModel).filter_by(id=appointment_id).first()
            if not appointment:
                return False
            
            # Only update provided fields
            if service_id is not None:
                appointment.service_id = service_id
            if slot_id is not None:
                appointment.slot_id = slot_id
            if google_event_id is not None:
                appointment.google_event_id = google_event_id

            db.session.commit()
            db.session.refresh(appointment)
            return AppointmentRepository._to_entity(appointment)
        
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update appointment: {str(e)}"}
    
        
    
    @staticmethod
    def update_status(appointment_id, status):
        appointment = db.session.query(AppointmentModel).filter_by(id=appointment_id).first()
        if appointment:
            appointment.status = status
            db.session.commit()
            db.session.refresh(appointment)
            return True
        return False
    

