class appointmentEntity:
    def __init__(self, id=None, client_id=None, service_id=None, slot_id=None, payment_id=None, google_event_id=None, created_at=None, status="booked"):
        self.id = id
        self.client_id = client_id
        self.service_id = service_id
        self.slot_id = slot_id
        self.payment_id = payment_id
        self.google_event_id = google_event_id
        self.created_at = created_at
        self.status = status