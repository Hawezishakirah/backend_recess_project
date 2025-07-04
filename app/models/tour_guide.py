from app.extensions import db
from datetime import datetime

class Tour_guide(db.Model):
    __tablename__="tour_guide"
    id = db.Column(db.Integer,primary_key=True)
    full_names = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(255),nullable=False)
    biography = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())

    def __init__(self,full_names,email,phone_number,language,biography,image):
        super(Tour_guide, self).__init__()
        self.full_names = full_names
        self.email = email
        self.biography = biography
        self.image = image
        self.phone_number = phone_number
        self.language = language
      
       
    def __repr__(self):
        return f'Tour_guide {self.phone_number}'
