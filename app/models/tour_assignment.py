from app.extensions import db
from datetime import datetime

class TourAssignment(db.Model):
    __tablename__ = "tour_assignment"
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_date = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __init__(self, assignment_date):
        super(TourAssignment, self).__init__()
        self.assignment_date = assignment_date
        
    def __repr__(self):
        return f'TourAssignment({self.assignment_date})'
