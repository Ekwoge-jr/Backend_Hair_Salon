from flask import Blueprint, request, jsonify
from app import db
from app.models.repositories.service_repo import ServiceRepository
from app.models.entities.service import serviceEntity
from app.services.user_service import UserService
from app.models.entities.user import userEntity


user_bp = Blueprint("user_bp", __name__)

# repo = ServiceRepository(db.session)

@user_bp.route("/create-service", methods= ["POST"])
def create_service():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    address = data.get("address")
    password = data.get("password")
    
    
    try:
        result=  UserService.create_user(first_name, last_name, email, phone_number, address, password)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/get", methods=["GET"])
def select():
    try:
        results = UserService.get_all_users()
        return jsonify([r.to_dict() for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@user_bp.route("/update/<int:user_id>", methods=["POST"])
def update(user_id):
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    address = data.get("address")
    password = data.get("password")
    try:
        results = UserService.update_user(user_id,first_name,last_name,email,phone_number,address,password)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route("/update_role/<int:user_id>", methods=["POST"])
def status(user_id):
    return UserService.update_user(user_id, role="stylist")