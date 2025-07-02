from app.extentions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__="customer"
    id = db.Column(db.Integer,primary_key=True)
    booking_date = db.Column(db.Integer,nullable=False)
    number_of_people= db.Column(db.Integer,nullable=False)
    total_price = db.Column(db.String(100),nullable=False,default='UGX')
    status = db.Column(db.Date,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,booking_date,number_of_people,total_price,status):
        super(Booking, self).__init__()
        self.booking_date = booking_date
        self.number_of_people = number_of_people
        self.total_price = total_price
        self.status = status

       
    def __repr__(self):
        return f'Customer {self.title}'
