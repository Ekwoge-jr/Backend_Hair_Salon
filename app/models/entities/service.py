class serviceEntity:
    def __init__(self, id=None, name=None, description=None, price=None, duration=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.duration = duration

    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "duration": self.duration,
            "description": self.description
        }