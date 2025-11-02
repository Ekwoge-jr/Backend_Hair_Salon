from app.models.repositories.payment_repo import PaymentRepository
from app.models.entities.payment import paymentEntity
from app.integrations.stripe import create_payment_intent


class PaymentService:

    @staticmethod
    def create_payment(amount, currency, metadata):
        
        # make payment intent in stripe
        payment_intent = create_payment_intent(amount, currency, metadata)


        # save the payment to our database
        payment = paymentEntity(
        stripe_id = payment_intent["id"],
        amount = payment_intent["amount"] / 100,  # convert from cents
        currency = payment_intent["currency"],
        status = payment_intent["status"]
        )
        
        return PaymentRepository.save_payment(payment)