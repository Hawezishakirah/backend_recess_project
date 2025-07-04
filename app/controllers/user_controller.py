from flask import Blueprint, request, jsonify
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from app.models.users import User
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from app.extensions import db, bcrypt


# Blueprint for user routes
users = Blueprint('users', __name__, url_prefix='/api/v1/users')


# Get all users (admin only)
@users.get('/')
@jwt_required()
def get_all_users():
    try:
        all_users = User.query.all()
        users_data = []

        for user in all_users:
            users_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.get_full_name(),
                'email': user.email,
                'contact': user.contact,
                'role': user.user_type,   # traveler, guide, agent, admin
                'languages': user.languages,
                'created_at': user.created_at
            })

        return jsonify({
            "message": "All users retrieved successfully",
            "total_users": len(all_users),
            "users": users_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all guides
@users.get('/guides')
@jwt_required()
def get_all_guides():
    try:
        all_guides = User.query.filter_by(user_type='guide').all()
        guides_data = []

        for guide in all_guides:
            guides_data.append({
                'id': guide.id,
                'first_name': guide.first_name,
                'last_name': guide.last_name,
                'username': guide.get_full_name(),
                'email': guide.email,
                'contact': guide.contact,
                'bio': guide.biography,
                'languages': guide.languages,
                'experience_years': guide.experience_years,
                'created_at': guide.created_at
            })

        return jsonify({
            "message": "All guides retrieved successfully",
            "total_guides": len(guides_data),
            "guides": guides_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get a user by ID
@users.get('/user/<int:id>')
@jwt_required()
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if not user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.get_full_name(),
            'email': user.email,
            'contact': user.contact,
            'role': user.user_type,
            'bio': user.biography,
            'languages': user.languages,
            'experience_years': getattr(user, 'experience_years', None),
            'created_at': user.created_at
        }

        return jsonify({
            "message": "User details retrieved successfully",
            "user": user_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Update user details (self or admin)
@users.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_user(id):
    try:
        current_user_id = get_jwt_identity()
        logged_in_user = User.query.filter_by(id=current_user_id).first()
        user = User.query.filter_by(id=id).first()

        if not user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        if logged_in_user.user_type != 'admin' and user.id != current_user_id:
            return jsonify({'error': 'Not authorized to update this user'}), HTTP_403_FORBIDDEN

        data = request.get_json()

        # Fields allowed to update
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.contact = data.get('contact', user.contact)
        user.biography = data.get('biography', user.biography)
        user.languages = data.get('languages', user.languages)
        user.user_type = data.get('user_type', user.user_type)
        user.experience_years = data.get('experience_years', getattr(user, 'experience_years', None))

        if "password" in data:
            hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
            user.password = hashed_password

        # Email and contact uniqueness checks
        if user.email != data.get('email', user.email):
            if User.query.filter_by(email=data.get('email')).first():
                return jsonify({'error': 'Email already in use'}), HTTP_409_CONFLICT

        if user.contact != data.get('contact', user.contact):
            if User.query.filter_by(contact=data.get('contact')).first():
                return jsonify({'error': 'Contact already in use'}), HTTP_409_CONFLICT

        db.session.commit()

        return jsonify({
            'message': f"{user.get_full_name()}'s details updated successfully",
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'contact': user.contact,
                'role': user.user_type,
                'bio': user.biography,
                'languages': user.languages,
                'experience_years': user.experience_years,
                'updated_at': user.updated_at
            }
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete a user (admin only)
@users.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    try:
        current_user_id = get_jwt_identity()
        logged_in_user = User.query.filter_by(id=current_user_id).first()
        user = User.query.filter_by(id=id).first()

        if not user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        if logged_in_user.user_type != 'admin':
            return jsonify({'error': 'Not authorized to delete user'}), HTTP_403_FORBIDDEN

        # Here, you can delete related records if applicable (e.g., bookings, tours)

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Search users by name and role (e.g., search guides)
@users.get('/search')
@jwt_required()
def search_users():
    try:
        search_query = request.args.get('query', '')
        role_filter = request.args.get('role', None)  # Optional: traveler, guide, agent

        query = User.query.filter(
            (User.first_name.ilike(f'%{search_query}%')) |
            (User.last_name.ilike(f'%{search_query}%'))
        )
        if role_filter:
            query = query.filter_by(user_type=role_filter)

        users_found = query.all()

        if not users_found:
            return jsonify({'message': 'No users found'}), HTTP_404_NOT_FOUND

        results = []
        for user in users_found:
            results.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.get_full_name(),
                'email': user.email,
                'contact': user.contact,
                'role': user.user_type,
                'languages': user.languages,
                'bio': user.biography,
                'experience_years': getattr(user, 'experience_years', None),
                'created_at': user.created_at
            })

        return jsonify({
            'message': f'Users matching "{search_query}" retrieved successfully',
            'total_results': len(results),
            'results': results
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
