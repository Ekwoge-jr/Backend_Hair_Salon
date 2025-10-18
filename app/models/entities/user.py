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