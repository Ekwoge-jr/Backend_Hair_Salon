import pytz


class slotEntity:
    def __init__(self, id=None, start_time=None, end_time=None, date=None, stylist_id=None, created_at=None, status="available"):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.stylist_id = stylist_id
        self.created_at = created_at    # added
        self.status = status


    # Converts the entity to a dictionary, which is json serialized
    def to_dict(self, user_tz="Africa/Douala"):
        tz = pytz.timezone(user_tz)
        return {
            "id": self.id,
            "start_time": self.start_time.astimezone(tz).strftime("%H:%M"),
            "end_time": self.end_time.astimezone(tz).strftime("%H:%M"),
            "date": self.date,
            "stylist_id": self.stylist_id,
            "created_at": self.created_at,  # added
            "status": self.status
        }