from app.extentions import db
from datetime import datetime

class Accomodation(db.Model):
    __tablename__="accomodation"
    id = db.Column(db.Integer,primary_key=True)
    full_names = db.Column(db.String(150),nullable=False)
    address = db.Column(db.String(100),nullable=False,default='UGX')
    type = db.Column(db.Date,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,full_names,address,type):
        super(Accomodation, self).__init__()
        self.full_names = full_names
        self.address = address
        self.type = type
       
    def __repr__(self):
        return f'Accomodation {self.full_names}'
