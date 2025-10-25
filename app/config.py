import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    # Database connection
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{os.getenv('password')}@localhost:3306/salon_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


     # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")