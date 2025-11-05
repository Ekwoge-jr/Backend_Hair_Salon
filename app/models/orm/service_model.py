from app import db

class ServiceModel(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)    