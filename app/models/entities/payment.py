class paymentEntity:
    def __init__(self, id=None, stripe_id=None, amount=None, currency=None, created_at=None, status=None):
        self.id = id
        self.stripe_id = stripe_id
        self.amount = amount
        self.currency = currency
        self.created_at = created_at
        self.status = status


    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self):
        return {
            "id": self.id,
            "stripe_id": self.stripe_id,
            "amount": self.amount,
            "currency": self.currency,
            "created_at": self.created_at,
            "status": self.status
        }