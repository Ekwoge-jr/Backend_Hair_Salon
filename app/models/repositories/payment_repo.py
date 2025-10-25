from app.models.orm.payment_model import PaymentModel
from app.models.entities.payment import paymentEntity
from sqlalchemy.orm import Session
from app import db

class PaymentRepository:


# conversion
    @staticmethod
    def _to_entity(model: PaymentModel):
        """Convert ORM model to Entity."""
        return paymentEntity(
            id = model.id,
            stripe_id = model.stripe_id,
            amount = model.amount,
            currency = model.currency,
            created_at = model.created_at,
            status = model.status
        )
  


# create
    @staticmethod
    def save_payment(entity: paymentEntity):
        new_payment = PaymentModel(
            stripe_id = entity.stripe_id,
            amount = entity.amount,
            currency = entity.currency,
            status = entity.status
        )
        db.session.add(new_payment)
        db.session.commit()
        db.session.refresh(new_payment)

        # Return the entity with ID set
        entity.id = new_payment.id
        return entity


# read
    @staticmethod
    def get_all_payments():
        results = db.session.query(PaymentModel).all()
        return [PaymentRepository._to_entity(payment) for payment in results]
    
    @staticmethod
    def get_payment_by_id(id):
        result = db.session.query(PaymentModel).filter(PaymentModel.id == id).first()
        return PaymentRepository._to_entity(result) if result else None
    
    @staticmethod
    def get_payment_by_status(status):
        results = db.session.query(PaymentModel).filter(PaymentModel.status == status).all()
        return [PaymentRepository._to_entity(payment) for payment in results]
    

# delete
    @staticmethod
    def delete_payment(id):
        payment = db.session.query(PaymentModel).filter_by(id=id).first()
        if payment:
            db.session.delete(payment)
            db.session.commit()
            return True
        return False