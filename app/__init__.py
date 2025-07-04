from flask import Flask
from app.extensions import db,migrate,jwt
from app.models import accomodations, booking, customer, payments, tour, tour_assignment, tour_guide, users


def create_app():

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)

    #importing models
    from app.models.users import User
    from app.models.customer import Customer
    from app.models.payments import Payment
    from app.models.accomodations import Accomodation
    from app.models.tour_assignment import Tour_assignment
    from app.models.tour import Tour
    from app.models.tour_guide import Tour_guide
    from app.models.booking import Booking
    
    
    
    #registering blue prints
    app.register_blueprint(customer)
    app.register_blueprint(accomodations)
    app.register_blueprint(payments)
    app.register_blueprint(tour_assignment)
    app.register_blueprint(tour)
    app.register_blueprint(tour_guide)
    app.register_blueprint(users)
    app.register_blueprint(booking)
    
    
    
    
    


    @app.route('/')
    def home():
        return ' API'


    return app