from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.accomodations import Accommodation
from app.models.users import User
from app.extensions import db

# Accommodations Blueprint
accommodations = Blueprint('accommodations', __name__, url_prefix='/api/v1/accommodations')

# Create an accommodation
@accommodations.route('/create', methods=['POST'])
@jwt_required()
def create_accommodation():
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    price = data.get('price')
    description = data.get('description')
    image = data.get('image')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    company_id = data.get('company_id')
    user_id = get_jwt_identity()

    if not name or not location or not price or not description or not start_date or not end_date or not company_id:
        return jsonify({'error': 'All fields are required'}), HTTP_400_BAD_REQUEST

    if Accommodation.query.filter_by(name=name, user_id=user_id).first():
        return jsonify({'error': 'You already created an accommodation with this name'}), HTTP_409_CONFLICT

    try:
        new_accommodation = Accommodation(
            name=name,
            location=location,
            price=price,
            description=description,
            image=image,
            start_date=start_date,
            end_date=end_date,
            company_id=company_id,
            user_id=user_id
        )
        db.session.add(new_accommodation)
        db.session.commit()

        return jsonify({
            'message': f'Accommodation "{name}" created successfully',
            'accommodation': {
                'name': new_accommodation.name,
                'location': new_accommodation.location,
                'price': new_accommodation.price,
                'description': new_accommodation.description,
                'image': new_accommodation.image,
                'start_date': new_accommodation.start_date,
                'end_date': new_accommodation.end_date,
                'company': {
                    'id': new_accommodation.company.id,
                    'name': new_accommodation.company.first_name,
                    'origin': new_accommodation.company.origin
                },
                'creator': {
                    'name': new_accommodation.user.get_full_name(),
                    'email': new_accommodation.user.email
                }
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all accommodations
@accommodations.route('/', methods=['GET'])
@jwt_required()
def get_all_accommodations():
    try:
        accommodations_list = Accommodation.query.all()
        data = []

        for acc in accommodations_list:
            data.append({
                'id': acc.id,
                'name': acc.name,
                'location': acc.location,
                'price': acc.price,
                'description': acc.description,
                'start_date': acc.start_date,
                'end_date': acc.end_date
            })

        return jsonify({
            'message': 'All accommodations retrieved successfully',
            'total': len(data),
            'accommodations': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get accommodation by ID
@accommodations.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_accommodation(id):
    try:
        acc = Accommodation.query.get(id)

        if not acc:
            return jsonify({'error': 'Accommodation not found'}), HTTP_404_NOT_FOUND

        return jsonify({
            'message': 'Accommodation details retrieved',
            'accommodation': {
                'name': acc.name,
                'location': acc.location,
                'price': acc.price,
                'description': acc.description,
                'start_date': acc.start_date,
                'end_date': acc.end_date
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Update accommodation
@accommodations.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_accommodation(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    acc = Accommodation.query.get(id)
    if not acc:
        return jsonify({'error': 'Accommodation not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and acc.user_id != current_user:
        return jsonify({'error': 'Not authorized to update this accommodation'}), HTTP_403_FORBIDDEN

    try:
        data = request.get_json()

        acc.name = data.get('name', acc.name)
        acc.location = data.get('location', acc.location)
        acc.price = data.get('price', acc.price)
        acc.description = data.get('description', acc.description)
        acc.image = data.get('image', acc.image)
        acc.start_date = data.get('start_date', acc.start_date)
        acc.end_date = data.get('end_date', acc.end_date)

        db.session.commit()

        return jsonify({'message': 'Accommodation updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete accommodation
@accommodations.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_accommodation(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    acc = Accommodation.query.get(id)
    if not acc:
        return jsonify({'error': 'Accommodation not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and acc.user_id != current_user:
        return jsonify({'error': 'Not authorized to delete this accommodation'}), HTTP_403_FORBIDDEN

    try:
        db.session.delete(acc)
        db.session.commit()
        return jsonify({'message': 'Accommodation deleted successfully'}), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
