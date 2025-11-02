import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_payment_intent(amount, currency="usd", metadata=None):

    # Creates a Stripe PaymentIntent and returns important details.    
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe expects cents
            currency=currency,
            metadata=metadata,
            automatic_payment_methods={"enabled": True}
        )

        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "amount": intent.amount,
            "currency": intent.currency,
            "status": intent.status,
            "metadata": intent.metadata
        }
        
    except Exception as e:
        raise Exception(f"Stripe error: {str(e)}")
    