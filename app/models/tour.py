from app.extentions import db
from datetime import datetime

class Tour(db.Model):
    __tablename__ = 'tour'
    id = db.Column(db.Integer,primary_key=True)
    tour_name = db.Column(db.String(100),unique=True)
    destination = db.Column(db.Text(),nullable=False)
    start_date = db.Column(db.Text(),nullable=False)
    end_date= db.Column(db.Integer,nullable=False)
    price = db.Column(db.String(100),nullable=False,default='UGX')
    max_group_size = db.Column(db.Date,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,tour_name,destination,start_date,end_date,price,max_group_size):
        super(Tour, self).__init__()
        self.tour_name = tour_name
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.price = price
        self.price = price


    def __repr__(self):
        return f'{self.name} {self.destination}'
    
        
    