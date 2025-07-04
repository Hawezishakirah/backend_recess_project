from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.users import User
from app.extensions import db

customers = Blueprint('customers', __name__, url_prefix='/api/v1/customers')

@customers.route('/', methods=['GET'])
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
        data = []

        for customer in customers_list:
            data.append({
                'id': customer.id,
                'name': customer.get_full_name(),
                'email': customer.email,
                'phone': customer.phone,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            })

        return jsonify({
            'message': 'All customers retrieved successfully',
            'total': len(data),
            'customers': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@customers.route('/<int:id>', methods=['GET'])
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


@customers.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_customer(id):
    current_user = get_jwt_identity()
    if current_user != id:
        return jsonify({'error': 'Not authorized to update this profile'}), HTTP_403_FORBIDDEN

    customer = User.query.get(id)
    if not customer or customer.user_type != 'customer':
        return jsonify({'error': 'Customer not found'}), HTTP_404_NOT_FOUND

    try:
        data = request.get_json()

        customer.first_name = data.get('first_name', customer.first_name)
        customer.last_name = data.get('last_name', customer.last_name)
        customer.phone = data.get('phone', customer.phone)
        customer.email = data.get('email', customer.email)

        db.session.commit()

        return jsonify({'message': 'Customer profile updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@customers.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user:
        return jsonify({'error': 'User not found'}), HTTP_401_UNAUTHORIZED

    customer = User.query.get(id)
    if not customer or customer.user_type != 'customer':
        return jsonify({'error': 'Customer not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and current_user != id:
        return jsonify({'error': 'Not authorized to delete this account'}), HTTP_403_FORBIDDEN

    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer account deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
