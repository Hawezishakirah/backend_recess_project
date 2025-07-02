from app.extentions import db
from datetime import datetime

class Payment(db.Model):
    __tablename__="payment"
    id = db.Column(db.Integer,primary_key=True)
    payment_date = db.Column(db.String(150),nullable=False)
    amount = db.Column(db.Integer,nullable=False)
    payment_method= db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,payment_date,amount,payment_method):
        super(Payment, self).__init__()
        self.payment_date = payment_date
        self.amount = amount
        self.payment_method = payment_method
        
    def __repr__(self):
        return f'Customer {self.title}'
