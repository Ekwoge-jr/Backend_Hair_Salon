class paymentEntity:
    def __init__(self, id=None, stripe_id=None, amount=None, currency=None, stylist_id=None, created_at=None, status="available"):
        self.id = id
        self.stripe_id = stripe_id
        self.amount = amount
        self.currency = currency
        self.stylist_id = stylist_id
        self.created_at = created_at
        self.status = status