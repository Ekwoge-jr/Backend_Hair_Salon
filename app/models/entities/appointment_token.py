class tokenEntity:
    def __init__(self, id=None, appointment_id=None, token=None, expires_at=None):
        self.id = id
        self.appointment_id = appointment_id
        self.token = token
        self.expires_at = expires_at
        


    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "token": self.token,
            "expires_at": self.expires_at,
        }