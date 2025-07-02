from app.extentions import db
from datetime import datetime

class Customer(db.Model):
    __tablename__="customer"
    id = db.Column(db.Integer,primary_key=True)
    full_names = db.Column(db.String(150),nullable=False)
    email = db.Column(db.Integer,nullable=False)
    phone_number= db.Column(db.Integer,nullable=False)
    address = db.Column(db.String(100),nullable=False,default='UGX')
    passport_number = db.Column(db.Date,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,full_names,email,phone_number,address,passport_number):
        super(Customer, self).__init__()
        self.full_names = full_names
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.passport_number = passport_number
       
    def __repr__(self):
        return f'Customer {self.title}'



    
