from app.extentions import db
from datetime import datetime

class Tour_assignment(db.Model):
    __tablename__="tour_assignment"
    id = db.Column(db.Integer,primary_key=True)
    assignment_date = db.Column(db.String(150),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,assignment_date):
        super(Tour_assignment, self).__init__()
        self.assignment_date = assignment_date
        
       
    def __repr__(self):
        return f'Tour_assignment {self.title}'
