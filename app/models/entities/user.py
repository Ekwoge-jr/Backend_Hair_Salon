class userEntity:
    def __init__(self, id=None, full_name=None, email=None, phone_number=None, password=None, role="client"):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.role = role


    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "password": self.password,
            "role": self.role
        }