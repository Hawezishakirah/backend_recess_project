from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.booking import Booking
from app.models.booking import Booking
from app.models.users import User
from app.extensions import db

# Bookings Blueprint
bookings = Blueprint('bookings', __name__, url_prefix='/api/v1/bookings')

# Create a booking
@bookings.route('/create', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json()
    accommodation_id = data.get('accommodation_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    guests = data.get('guests')
    user_id = get_jwt_identity()

    if not accommodation_id or not start_date or not end_date or not guests:
        return jsonify({'error': 'All fields are required'}), HTTP_400_BAD_REQUEST

    accommodation = accommodation.query.get(accommodation_id)
    if not accommodation:
        return jsonify({'error': 'Accommodation not found'}), HTTP_404_NOT_FOUND

    try:
        new_booking = Booking(
            user_id=user_id,
            accommodation_id=accommodation_id,
            start_date=start_date,
            end_date=end_date,
            guests=guests
        )
        db.session.add(new_booking)
        db.session.commit()

        return jsonify({
            'message': 'Booking created successfully',
            'booking': {
                'id': new_booking.id,
                'accommodation': {
                    'id': accommodation.id,
                    'name': accommodation.name,
                    'location': accommodation.location
                },
                'start_date': new_booking.start_date,
                'end_date': new_booking.end_date,
                'guests': new_booking.guests
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all bookings
@bookings.route('/', methods=['GET'])
@jwt_required()
def get_all_bookings():
    try:
        bookings_list = Booking.query.all()
        data = []

        for booking in bookings_list:
            data.append({
                'id': booking.id,
                'user': booking.user.get_full_name(),
                'accommodation': booking.accommodation.name,
                'start_date': booking.start_date,
                'end_date': booking.end_date,
                'guests': booking.guests
            })

        return jsonify({
            'message': 'All bookings retrieved successfully',
            'total': len(data),
            'bookings': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get booking by ID
@bookings.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_booking(id):
    try:
        booking = Booking.query.get(id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), HTTP_404_NOT_FOUND

        return jsonify({
            'message': 'Booking details retrieved',
            'booking': {
                'id': booking.id,
                'user': booking.user.get_full_name(),
                'accommodation': {
                    'id': booking.accommodation.id,
                    'name': booking.accommodation.name,
                    'location': booking.accommodation.location
                },
                'start_date': booking.start_date,
                'end_date': booking.end_date,
                'guests': booking.guests
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Update booking
@bookings.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_booking(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    booking = Booking.query.get(id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and booking.user_id != current_user:
        return jsonify({'error': 'Not authorized to update this booking'}), HTTP_403_FORBIDDEN

    try:
        data = request.get_json()
        booking.start_date = data.get('start_date', booking.start_date)
        booking.end_date = data.get('end_date', booking.end_date)
        booking.guests = data.get('guests', booking.guests)

        db.session.commit()

        return jsonify({'message': 'Booking updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete booking
@bookings.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_booking(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    booking = Booking.query.get(id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and booking.user_id != current_user:
        return jsonify({'error': 'Not authorized to delete this booking'}), HTTP_403_FORBIDDEN

    try:
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Booking deleted successfully'}), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
