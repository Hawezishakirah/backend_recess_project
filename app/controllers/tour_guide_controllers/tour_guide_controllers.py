from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.users import User
from app.extensions import db

# Tour Guides Blueprint
tour_guides = Blueprint('tour_guides', __name__, url_prefix='/api/v1/tour-guides')


# Create a new tour guide (admin only)
@tour_guides.route('/create', methods=['POST'])
@jwt_required()
def create_tour_guide():
    current_user = get_jwt_identity()
    admin = User.query.get(current_user)

    if admin.user_type != 'admin':
        return jsonify({'error': 'Only admin can create tour guides'}), HTTP_403_FORBIDDEN

    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')  # Assume hashed later in model or helper

    if not first_name or not last_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User with this email already exists'}), HTTP_409_CONFLICT

    try:
        new_guide = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            user_type='guide'
        )
        db.session.add(new_guide)
        db.session.commit()

        return jsonify({
            'message': 'Tour guide created successfully',
            'guide': {
                'id': new_guide.id,
                'name': new_guide.get_full_name(),
                'email': new_guide.email
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all tour guides (admin only)
@tour_guides.route('/', methods=['GET'])
@jwt_required()
def get_all_tour_guides():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can view all tour guides'}), HTTP_403_FORBIDDEN

    try:
        guides = User.query.filter_by(user_type='guide').all()
        data = []

        for guide in guides:
            data.append({
                'id': guide.id,
                'name': guide.get_full_name(),
                'email': guide.email
            })

        return jsonify({
            'message': 'All tour guides retrieved successfully',
            'total': len(data),
            'guides': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get tour guide by ID (admin or self)
@tour_guides.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_tour_guide(id):
    guide = User.query.get(id)

    if not guide or guide.user_type != 'guide':
        return jsonify({'error': 'Tour guide not found'}), HTTP_404_NOT_FOUND

    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin' and user.id != guide.id:
        return jsonify({'error': 'Not authorized to view this guide'}), HTTP_403_FORBIDDEN

    return jsonify({
        'message': 'Tour guide details retrieved',
        'guide': {
            'id': guide.id,
            'name': guide.get_full_name(),
            'email': guide.email
        }
    }), HTTP_200_OK


# Update tour guide (admin or self)
@tour_guides.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_tour_guide(id):
    guide = User.query.get(id)
    if not guide or guide.user_type != 'guide':
        return jsonify({'error': 'Tour guide not found'}), HTTP_404_NOT_FOUND

    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin' and user.id != guide.id:
        return jsonify({'error': 'Not authorized to update this guide'}), HTTP_403_FORBIDDEN

    try:
        data = request.get_json()
        guide.first_name = data.get('first_name', guide.first_name)
        guide.last_name = data.get('last_name', guide.last_name)
        guide.email = data.get('email', guide.email)

        db.session.commit()
        return jsonify({'message': 'Tour guide updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete tour guide (admin only)
@tour_guides.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_tour_guide(id):
    current_user = get_jwt_identity()
    admin = User.query.get(current_user)

    if admin.user_type != 'admin':
        return jsonify({'error': 'Only admin can delete guides'}), HTTP_403_FORBIDDEN

    guide = User.query.get(id)
    if not guide or guide.user_type != 'guide':
        return jsonify({'error': 'Tour guide not found'}), HTTP_404_NOT_FOUND

    try:
        db.session.delete(guide)
        db.session.commit()
        return jsonify({'message': 'Tour guide deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
