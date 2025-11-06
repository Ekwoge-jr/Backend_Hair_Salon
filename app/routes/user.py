from flask import Blueprint, request, jsonify
from app import db
import re
from app.services.user_service import UserService


user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/create-user", methods= ["POST"])
def create_user():

    """
    Create a new user
    ---
    tags:
      - Users
    description: Creates a new user with full name, email, phone number, and password.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            full_name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
            phone_number:
              type: string
              example: +237654321987
            password:
              type: string
              example: SecurePass123
    responses:
      200:
        description: User created successfully.
      400:
        description: Invalid input or user creation failed.
    """


    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return {"message": "Invalid email address!"}
    elif not re.match(r'[A-Za-z]+', full_name):
        return {"message": "Username must contain only characters!"}
    elif not full_name:
        return {"message": "Please enter your full name!"}
    elif not email:
        return {"message": "Please enter your email!"}
    
    try:
        result=  UserService.create_user(full_name, email, phone_number, password)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@user_bp.route("/update/<int:user_id>", methods=["PUT"])
def update(user_id):

    """
    Update user details
    ---
    tags:
      - Users
    description: Updates a user's information such as name, email, phone number, password, or role.
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: Unique ID of the user to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            full_name:
              type: string
              example: Jane Doe
            email:
              type: string
              example: jane@example.com
            phone_number:
              type: string
              example: +237654987321
            password:
              type: string
              example: NewPass456
            role:
              type: string
              example: admin
    responses:
      200:
        description: User updated successfully.
      400:
        description: Invalid input or user not found.
    """
     
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    role = data.get("role")

    if email:
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return {"message": "Invalid email address!"}
    elif full_name:
        if not re.match(r'[A-Za-z]+', full_name):
            return {"message": "Username must contain only characters!"}
    
    try:
        results = UserService.update_user(user_id,full_name,email,phone_number,password,role)
        return jsonify(results.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@user_bp.route("/get_users", methods=["GET"])
def get_users():

    """
    Retrieve all users
    ---
    tags: 
      - Users
    description: Fetches a list of all registered users from the database.
    responses:
      200:
        description: List of users retrieved successfully.
        content: 
          application/json: 
            schema:
              type: array
              items:
                type: object
              properties:
                id: 
                  type: integer
                  example: 1
                full_name: 
                  type: string
                  example: John Doe
                email: 
                  type: string
                  example: john@example.com
                phone_number: 
                  type: string
                  example: +237654321987
                role: 
                  type: string
                  example: client
      400: 
        description: Error retrieving users.
    """
    try:
        results = UserService.get_all_users()
        return jsonify([r.to_dict() for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 400
