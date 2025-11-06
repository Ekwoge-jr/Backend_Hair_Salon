from flask import Blueprint, request, jsonify
from app.models.repositories.user_repo import UserRepository
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

      # You can later add JWT generation here
      return jsonify({
          "message": "Login successful",
          "user": {
              "id": user.id,
              "full_name": user.full_name,
              "role": user.role
          }
      }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400