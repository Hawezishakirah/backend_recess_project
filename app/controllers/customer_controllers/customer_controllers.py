from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.users import User
from app.extensions import db

customer = Blueprint('customer', __name__, url_prefix='/api/v1/customer')# "customer" has to match blueprint registration

@customer.route('/', methods=['GET'])
@jwt_required()
def get_all_customers():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user:
        return jsonify({'error': 'User not found'}), HTTP_401_UNAUTHORIZED

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can view customers'}), HTTP_403_FORBIDDEN

    try:
        customers_list = User.query.filter_by(user_type='customer').all()
        data = [
            {
                'id': customer.id,
                'name': customer.get_full_name(),
                'email': customer.email,
                'phone': customer.phone,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            }
            for customer in customers_list
        ]

        return jsonify({
            'message': 'All customers retrieved successfully',
            'total': len(data),
            'customers': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@customer.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_customer(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user:
        return jsonify({'error': 'User not found'}), HTTP_401_UNAUTHORIZED

    customer = User.query.get(id)
    if not customer or customer.user_type != 'customer':
        return jsonify({'error': 'Customer not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and current_user != customer.id:
        return jsonify({'error': 'Not authorized to view this customer'}), HTTP_403_FORBIDDEN

    try:
        return jsonify({
            'message': 'Customer details retrieved',
            'customer': {
                'id': customer.id,
                'name': customer.get_full_name(),
                'email': customer.email,
                'phone': customer.phone,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@customer.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_customer(id):
    current_user = get_jwt_identity()
    if current_user != id:
        return jsonify({'error': 'Not authorized to update this profile'}), HTTP_403_FORBIDDEN

    customer_user = User.query.get(id)
    if not customer_user or customer_user.user_type != 'customer':
        return jsonify({'error': 'Customer not found'}), HTTP_404_NOT_FOUND

    try:
        data = request.get_json()
        customer_user.first_name = data.get('first_name', customer_user.first_name)
        customer_user.last_name = data.get('last_name', customer_user.last_name)
        customer_user.phone = data.get('phone', customer_user.phone)
        customer_user.email = data.get('email', customer_user.email)

        db.session.commit()

        return jsonify({'message': 'Customer profile updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@customer.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user:
        return jsonify({'error': 'User not found'}), HTTP_401_UNAUTHORIZED

    customer_user = User.query.get(id)
    if not customer_user or customer_user.user_type != 'customer':
        return jsonify({'error': 'Customer not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and current_user != id:
        return jsonify({'error': 'Not authorized to delete this account'}), HTTP_403_FORBIDDEN

    try:
        db.session.delete(customer_user)
        db.session.commit()
        return jsonify({'message': 'Customer account deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
