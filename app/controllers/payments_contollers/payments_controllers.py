from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.payments import Payment
from app.models.booking import Booking
from app.models.users import User
from app.extensions import db

# Payments Blueprint
payments = Blueprint('payments', __name__, url_prefix='/api/v1/payments')

# Create a payment
@payments.route('/create', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json()
    booking_id = data.get('booking_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method')
    status = data.get('status', 'pending')
    user_id = get_jwt_identity()

    if not booking_id or not amount or not payment_method:
        return jsonify({'error': 'All fields are required'}), HTTP_400_BAD_REQUEST

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), HTTP_404_NOT_FOUND

    if booking.user_id != user_id:
        return jsonify({'error': 'Not authorized to pay for this booking'}), HTTP_403_FORBIDDEN

    try:
        new_payment = Payment(
            user_id=user_id,
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            status=status
        )
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({
            'message': 'Payment created successfully',
            'payment': {
                'id': new_payment.id,
                'amount': new_payment.amount,
                'payment_method': new_payment.payment_method,
                'status': new_payment.status,
                'booking_id': new_payment.booking_id
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all payments (admin only)
@payments.route('/', methods=['GET'])
@jwt_required()
def get_all_payments():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can view all payments'}), HTTP_403_FORBIDDEN

    try:
        payments_list = Payment.query.all()
        data = []

        for pay in payments_list:
            data.append({
                'id': pay.id,
                'user': pay.user.get_full_name(),
                'booking_id': pay.booking_id,
                'amount': pay.amount,
                'payment_method': pay.payment_method,
                'status': pay.status,
                'timestamp': pay.timestamp
            })

        return jsonify({
            'message': 'All payments retrieved successfully',
            'total': len(data),
            'payments': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get payment by ID
@payments.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_payment(id):
    current_user = get_jwt_identity()
    payment = Payment.query.get(id)

    if not payment:
        return jsonify({'error': 'Payment not found'}), HTTP_404_NOT_FOUND

    if payment.user_id != current_user and User.query.get(current_user).user_type != 'admin':
        return jsonify({'error': 'Not authorized to view this payment'}), HTTP_403_FORBIDDEN

    try:
        return jsonify({
            'message': 'Payment details retrieved',
            'payment': {
                'id': payment.id,
                'booking_id': payment.booking_id,
                'amount': payment.amount,
                'payment_method': payment.payment_method,
                'status': payment.status,
                'timestamp': payment.timestamp
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Update payment status (admin only)
@payments.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_payment(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can update payment status'}), HTTP_403_FORBIDDEN

    payment = Payment.query.get(id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), HTTP_404_NOT_FOUND

    try:
        data = request.get_json()
        payment.status = data.get('status', payment.status)
        db.session.commit()

        return jsonify({'message': 'Payment updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete payment (admin only)
@payments.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_payment(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can delete payments'}), HTTP_403_FORBIDDEN

    payment = Payment.query.get(id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), HTTP_404_NOT_FOUND

    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': 'Payment deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
