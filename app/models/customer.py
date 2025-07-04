from app.extensions import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    full_names = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)  # Changed to String for emails
    phone_number = db.Column(db.String(20), nullable=False)  # Phone numbers should be strings (to allow +, - etc)
    address = db.Column(db.String(100), nullable=False, default='UGX')
    passport_number = db.Column(db.String(50), nullable=False)
    biography = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Use utcnow (no parentheses)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Same here

    def __init__(self, full_names, email, phone_number, address, passport_number, biography, image=None):
        super().__init__()
        self.full_names = full_names
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.passport_number = passport_number
        self.biography = biography
        self.image = image

    def __repr__(self):
        return f'<Customer {self.full_names}>'
