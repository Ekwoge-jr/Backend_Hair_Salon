class userEntity:
    def __init__(self, id=None, full_name=None, email=None, phone_number=None, password=None, role="client", google_access_token=None, google_refresh_token=None, google_token_expiry=None, is_active = True ):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.role = role
        self.is_active = is_active

        self.google_access_token = google_access_token
        self.google_refresh_token = google_refresh_token
        self.google_token_expiry = google_token_expiry


    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "password": self.password,
            "role": self.role,
            "is_active": self.is_active,
            "google_access_token": self.google_access_token,
            "google_refresh_token": self.google_refresh_token,
            "google_token_expiry": self.google_token_expiry
        }