class slotEntity:
    def __init__(self, id=None, start_time=None, end_time=None, date=None, stylist_id=None, status="available"):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.stylist_id = stylist_id
        self.status = status


    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "date": self.date,
            "stylist_id": self.stylist_id,
            "status": self.status
        }