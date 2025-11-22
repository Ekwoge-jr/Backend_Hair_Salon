from flask import Blueprint, request, jsonify, session
from app.models.repositories.user_repo import UserRepository
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity  
from app import bcrypt, db

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Admin/Stylist login
    ---
    tags:
      - Authentication
    description: Authenticates an admin or stylist using email and password.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: admin@example.com
            password:
              type: string
              example: secret123
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
      user = UserRepository.get_users_by_email(email)
      if not user:
          return jsonify({"error": "User not found"}), 404

      # ✅ Verify the password
      if not bcrypt.check_password_hash(user.password, password):
          return jsonify({"error": "Incorrect password"}), 401

      # Create JWT tokens
      access_token = create_access_token(identity = {"id": user.id, "role": user.role})
      refresh_token = create_refresh_token(identity = {"id": user.id, "role": user.role})

      # You can later add JWT generation here
      return jsonify({
          "message": "Login successful",
          "user": {
              "id": user.id,
              "full_name": user.full_name,
              "role": user.role,
              "access_token": access_token,
              "refresh_token": refresh_token
          }
      }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    return {"access_token": new_access}