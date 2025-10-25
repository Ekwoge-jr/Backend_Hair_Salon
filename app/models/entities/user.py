class userEntity:
    def __init__(self, id=None, first_name=None, last_name=None, email=None, phone_number=None, address=None,  password=None, role="client"):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.password = password
        self.role = role


    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "password": self.password,
            "role": self.role
        }