from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.tour_assignment import TourAssignment
from app.models.tour import Tour
from app.models.users import User
from app.extensions import db

# Tour Assignments Blueprint
tour_assignments = Blueprint('tour_assignments', __name__, url_prefix='/api/v1/tour-assignments')

# Create a tour assignment
@tour_assignments.route('/create', methods=['POST'])
@jwt_required()
def create_tour_assignment():
    data = request.get_json()
    tour_id = data.get('tour_id')
    guide_id = data.get('guide_id')
    assignment_date = data.get('assignment_date')
    current_user = get_jwt_identity()

    user = User.query.get(current_user)
    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can assign tours'}), HTTP_403_FORBIDDEN

    if not tour_id or not guide_id or not assignment_date:
        return jsonify({'error': 'All fields are required'}), HTTP_400_BAD_REQUEST

    try:
        new_assignment = TourAssignment(
            tour_id=tour_id,
            guide_id=guide_id,
            assignment_date=assignment_date
        )
        db.session.add(new_assignment)
        db.session.commit()

        return jsonify({
            'message': 'Tour assignment created successfully',
            'assignment': {
                'id': new_assignment.id,
                'tour_id': new_assignment.tour_id,
                'guide_id': new_assignment.guide_id,
                'assignment_date': new_assignment.assignment_date
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all tour assignments (admin only)
@tour_assignments.route('/', methods=['GET'])
@jwt_required()
def get_all_tour_assignments():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can view all tour assignments'}), HTTP_403_FORBIDDEN

    try:
        assignments = TourAssignment.query.all()
        data = []

        for ta in assignments:
            data.append({
                'id': ta.id,
                'tour': {
                    'id': ta.tour.id,
                    'name': ta.tour.name
                },
                'guide': {
                    'id': ta.guide.id,
                    'name': ta.guide.get_full_name()
                },
                'assignment_date': ta.assignment_date
            })

        return jsonify({
            'message': 'All tour assignments retrieved successfully',
            'total': len(data),
            'assignments': data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get assignment by ID
@tour_assignments.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_tour_assignment(id):
    assignment = TourAssignment.query.get(id)
    if not assignment:
        return jsonify({'error': 'Tour assignment not found'}), HTTP_404_NOT_FOUND

    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin' and assignment.guide_id != current_user:
        return jsonify({'error': 'Not authorized to view this assignment'}), HTTP_403_FORBIDDEN

    return jsonify({
        'message': 'Tour assignment details retrieved',
        'assignment': {
            'id': assignment.id,
            'tour': {
                'id': assignment.tour.id,
                'name': assignment.tour.name
            },
            'guide': {
                'id': assignment.guide.id,
                'name': assignment.guide.get_full_name()
            },
            'assignment_date': assignment.assignment_date
        }
    }), HTTP_200_OK


# Update assignment (admin only)
@tour_assignments.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_tour_assignment(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can update assignments'}), HTTP_403_FORBIDDEN

    assignment = TourAssignment.query.get(id)
    if not assignment:
        return jsonify({'error': 'Tour assignment not found'}), HTTP_404_NOT_FOUND

    try:
        data = request.get_json()
        assignment.tour_id = data.get('tour_id', assignment.tour_id)
        assignment.guide_id = data.get('guide_id', assignment.guide_id)
        assignment.assignment_date = data.get('assignment_date', assignment.assignment_date)

        db.session.commit()
        return jsonify({'message': 'Tour assignment updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete assignment (admin only)
@tour_assignments.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_tour_assignment(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if user.user_type != 'admin':
        return jsonify({'error': 'Only admin can delete assignments'}), HTTP_403_FORBIDDEN

    assignment = TourAssignment.query.get(id)
    if not assignment:
        return jsonify({'error': 'Tour assignment not found'}), HTTP_404_NOT_FOUND

    try:
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({'message': 'Tour assignment deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
