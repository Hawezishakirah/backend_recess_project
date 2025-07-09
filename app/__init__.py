from flask import Flask
from app.extensions import db, migrate, jwt

# Import Blueprints from controllers
from app.controllers.accommodation_controllers.accommodation_controllers import accommodations
from app.controllers.customer_controllers.customer_controllers import customer
from app.controllers.payments_contollers.payments_controllers import payments
from app.controllers.tour_assignment_controllers.tour_assignment_controllers import tour_assignments
from app.controllers.tour_controllers.tour_controllers import tours
from app.controllers.tour_guide_controllers.tour_guide_controllers import tour_guides
from app.controllers.user_controller.user_controller import users
from app.controllers.booking_controllers.booking_controllers import bookings
from app.models import accomodations

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Registering Blueprints
    app.register_blueprint(customer)
    app.register_blueprint(accommodations)
    app.register_blueprint(payments)
    app.register_blueprint(tour_assignments)
    app.register_blueprint(tours)
    app.register_blueprint(tour_guides)
    app.register_blueprint(users)
    app.register_blueprint(bookings)

    @app.route('/')
    def home():
        return 'API is running'

    return app
