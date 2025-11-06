from app import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(10), nullable=False, default="client")     # client, stylist/admin 