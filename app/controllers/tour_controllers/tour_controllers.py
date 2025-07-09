from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.tour import Tour
from app.models.users import User
from app.extensions import db


# Tours Blueprint
tours = Blueprint('tours', __name__, url_prefix='/api/v1/tours')

# Create a tour
@tours.route('/create', methods=['POST'])
@jwt_required()
def create_tour():
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

    if Tour.query.filter_by(name=name, user_id=user_id).first():
        return jsonify({'error': 'You already created a tour with this name'}), HTTP_409_CONFLICT

    try:
        new_tour = Tour(
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
        db.session.add(new_tour)
        db.session.commit()

        return jsonify({
            'message': f'Tour "{name}" created successfully',
            'tour': {
                'name': new_tour.name,
                'location': new_tour.location,
                'price': new_tour.price,
                'description': new_tour.description,
                'image': new_tour.image,
                'start_date': new_tour.start_date,
                'end_date': new_tour.end_date,
                'company': {
                    'id': new_tour.company.id,
                    'name': new_tour.company.first_name,
                    'origin': new_tour.company.origin
                },
                'creator': {
                    'name': new_tour.user.get_full_name(),
                    'email': new_tour.user.email
                }
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all tours
@tours.route('/', methods=['GET'])
@jwt_required()
def get_all_tours():
    try:
        tours_list = Tour.query.all()
        data = []

        for tour in tours_list:
            data.append({
                'id': tour.id,
                'name': tour.name,
                'location': tour.location,
                'price': tour.price,
                'description': tour.description,
                'start_date': tour.start_date,
                'end_date': tour.end_date
            })

        return jsonify({
            'message': 'All tours retrieved successfully',
            'total': len(data),
            'tours': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get tour by ID
@tours.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_tour(id):
    try:
        tour = Tour.query.get(id)

        if not tour:
            return jsonify({'error': 'Tour not found'}), HTTP_404_NOT_FOUND

        return jsonify({
            'message': 'Tour details retrieved',
            'tour': {
                'name': tour.name,
                'location': tour.location,
                'price': tour.price,
                'description': tour.description,
                'start_date': tour.start_date,
                'end_date': tour.end_date
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Update tour
@tours.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_tour(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    tour = Tour.query.get(id)
    if not tour:
        return jsonify({'error': 'Tour not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and tour.user_id != current_user:
        return jsonify({'error': 'Not authorized to update this tour'}), HTTP_403_FORBIDDEN

    try:
        data = request.get_json()

        tour.name = data.get('name', tour.name)
        tour.location = data.get('location', tour.location)
        tour.price = data.get('price', tour.price)
        tour.description = data.get('description', tour.description)
        tour.image = data.get('image', tour.image)
        tour.start_date = data.get('start_date', tour.start_date)
        tour.end_date = data.get('end_date', tour.end_date)

        db.session.commit()

        return jsonify({'message': 'Tour updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete tour
@tours.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_tour(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    tour = Tour.query.get(id)
    if not tour:
        return jsonify({'error': 'Tour not found'}), HTTP_404_NOT_FOUND

    if user.user_type != 'admin' and tour.user_id != current_user:
        return jsonify({'error': 'Not authorized to delete this tour'}), HTTP_403_FORBIDDEN

    try:
        db.session.delete(tour)
        db.session.commit()
        return jsonify({'message': 'Tour deleted successfully'}), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

