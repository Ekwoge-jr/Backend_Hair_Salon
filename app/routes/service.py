from flask import Blueprint, request, jsonify
from app import db
from app.services.service_service import ServiceService

from werkzeug.utils import secure_filename
from datetime import datetime
import os

from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

"""
service_bp = Blueprint("service_bp", __name__)


UPLOAD_FOLDER = "app/uploads/services"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Make sure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@service_bp.route("/create-service/<int:user_id>", methods= ["POST"])
# @cross_origin()
@jwt_required()
def create_service(user_id):

    """
"""
    Create a new service
    ---
    tags:
      - Services
    description: Uploads a service image and saves the service details in the database.
    consumes:
      - multipart/form-data
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the admin
      - name: name
        in: formData
        type: string
        required: true
        description: Name of the service
      - name: description
        in: formData
        type: string
        required: true
        description: Short description of the service
      - name: price
        in: formData
        type: number
        required: true
        description: Price of the service
      - name: duration
        in: formData
        type: integer
        required: true
        description: Duration of the service
      - name: image
        in: formData
        type: file
        required: true
        description: Image of the service (png, jpg, jpeg)
    responses:
      200:
        description: Service created successfully
      400:
        description: Invalid image format or missing data
    

    current_user = get_jwt_identity()
    print("--- AUTH DEBUG ---")
    print(f"Token Identity: {current_user}")
    print(f"URL user_id: {user_id}")
    print(f"Type of URL id: {type(user_id)}")

    if isinstance(current_user, dict):
        token_id = current_user.get("id")
        token_role = current_user.get("role")
    else:
        # If identity is just a string/int ID
        token_id = current_user
        token_role = "admin" # (You might need to fetch the user from DB to verify role here)

    # UPDATED CHECK: Ensure types match (both as integers)
    if int(token_id) != int(user_id) or token_role != "admin":
        return jsonify({
            "error": "Unauthorized",
            "msg": f"Token ID {token_id} doesn't match URL ID {user_id} or role isn't admin"
        }), 403
    # ensure only stylists can create slots
    if current_user["id"] != user_id or current_user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    image = request.files.get("image")
    duration = request.form.get("duration")

    if not all([name, description, price, image]):
        return jsonify({"error": "All fields are required"}), 400
    
    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid image format"}), 400
    
    # filename = secure_filename(image.filename)
    # save_path = os.path.join(UPLOAD_FOLDER, filename)
    # image.save(save_path)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    upload_path = os.path.join(base_dir, "uploads", "services")
    os.makedirs(upload_path, exist_ok=True)
        
    filename = secure_filename(image.filename)
    image.save(os.path.join(upload_path, filename))

    try:
        print("Files:", request.files)
        print("Form Data:", request.form)
        result=  ServiceService.create_service(name, description, price, filename, duration)
        return jsonify(result.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
"""
# import os
# from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
#from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.services.service_service import ServiceService

service_bp = Blueprint("service_bp", __name__)

# --- FIX: ROBUST PATH LOGIC ---
# This finds the actual root folder of your project on the cPanel server
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) 
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads", "services")

# Ensure the folder exists on startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_safe_identity(current_user):
    """Safely extracts info whether identity is a dict or a JSON string."""
    if isinstance(current_user, dict):
        return int(current_user.get("id")), current_user.get("role")
    # If for some reason it's still a raw stringified JSON
    import json
    try:
        data = json.loads(current_user)
        return int(data.get("id")), data.get("role")
    except:
        return None, None

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@service_bp.route("/create-service/<int:user_id>", methods=["POST"])
@jwt_required()
def create_service(user_id):
    current_user = get_jwt_identity()
    
    # --- FIX: UNIFIED IDENTITY CHECK ---
    # Handle both dictionary and string identities safely
    if isinstance(current_user, str):
        try:
            # Convert the string back into a real dictionary
            current_user = json.loads(current_user)
        except json.JSONDecodeError:
            # Fallback if the token only contains a plain ID string like "1"
            pass

    # 2. Now that we've ensured it's a dict, we can extract the data
    if isinstance(current_user, dict):
        token_id = int(current_user.get("id"))
        token_role = current_user.get("role")
    else:
        # Fallback for old tokens or simple identities
        token_id = int(current_user)
        token_role = "admin"

    # 3. Secure comparison
    if token_id != user_id or token_role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    # --- DATA COLLECTION ---
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    duration = request.form.get("duration")
    image = request.files.get("image")

    if not all([name, description, price, image, duration]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid image format"}), 400
    
    # --- FILE SAVING ---
    try:
        filename = secure_filename(image.filename)
        # Use the absolute path we defined at the top
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)
        
        # Call your service logic
        result = ServiceService.create_service(name, description, price, filename, duration)
        return jsonify(result.to_dict()), 200

    except Exception as e:
        # This will catch things like "Permission Denied" and return them as JSON
        # instead of a generic 500 error page
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500



@service_bp.route("/update/<int:user_id>/<int:service_id>", methods=["POST"])
@jwt_required() # ADDED
def update(user_id, service_id):

    """
    Update a service
    ---
    tags:
      - Services
    description: Updates an existing service and optionally replaces its image.
    consumes:
      - multipart/form-data
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the admin
      - name: service_id
        in: path
        type: integer
        required: true
        description: ID of the service to update
      - name: name
        in: formData
        type: string
        required: false
      - name: description
        in: formData
        type: string
        required: false
      - name: price
        in: formData
        type: number
        required: false
      - name: duration
        in: formData
        type: integer
        required: false
      - name: image
        in: formData
        type: file
        required: false
        description: New image for the service (png, jpg, jpeg)
    responses:
      200:
        description: Service updated successfully
      400:
        description: Error updating service
    """

    current_user = get_jwt_identity()
    
    # ensure only stylists can create slots
    # token_id, token_role = get_safe_identity(current_user)

    if isinstance(current_user, str):
        try:
            # Convert the string back into a real dictionary
            current_user = json.loads(current_user)
        except json.JSONDecodeError:
            # Fallback if the token only contains a plain ID string like "1"
            pass

    # 2. Now that we've ensured it's a dict, we can extract the data
    if isinstance(current_user, dict):
        token_id = int(current_user.get("id"))
        token_role = current_user.get("role")
    else:
        # Fallback for old tokens or simple identities
        token_id = int(current_user)
        token_role = "admin"

    # 3. Secure comparison
    if token_id != user_id or token_role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    if token_id != user_id or token_role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    image = request.files.get("image")
    duration = request.form.get("duration")

    filename = None
    if image:
        if not allowed_file(image.filename):
            return jsonify({"error": "Invalid image format"}), 400
        filename = secure_filename(image.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)
    
    try:
        results = ServiceService.update_service(service_id, name, description, price, filename, duration)
        return jsonify(results.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@service_bp.route("/get_services", methods=["GET"])
def get_services():

    """
    Retrieve all services
    ---
    tags: 
      - Services
    description: Fetches a list of all created services from the database.
    responses:
      200:
        description: List of services retrieved successfully.
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
                name: 
                  type: string
                  example: Braids
                description: 
                  type: string
                price: 
                  type: number
                duration: 
                  type: integer
                image:
                  type: string
      400: 
        description: Error retrieving services.
    """
    try:
        results = ServiceService.get_all_services()
        return jsonify([r.to_dict() for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@service_bp.route("/delete/<int:User_id>/<int:service_id>", methods=["DELETE"])
def delete_service(user_id,service_id):

    """
    Delete a service
    ---
    tags:
      - Services
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the admin
      - name: service_id
        in: path
        type: integer
        required: true
        description: ID of the service to delete
    responses:
      200:
        description: Service deleted successfully
      400:
        description: Error deleting service
    """

    current_user = get_jwt_identity()
    
    # ensure only stylists can create slots
    # token_id, token_role = get_safe_identity(current_user)
    if isinstance(current_user, str):
        try:
            # Convert the string back into a real dictionary
            current_user = json.loads(current_user)
        except json.JSONDecodeError:
            # Fallback if the token only contains a plain ID string like "1"
            pass

    # 2. Now that we've ensured it's a dict, we can extract the data
    if isinstance(current_user, dict):
        token_id = int(current_user.get("id"))
        token_role = current_user.get("role")
    else:
        # Fallback for old tokens or simple identities
        token_id = int(current_user)
        token_role = "admin"

    # 3. Secure comparison-
    
    if token_id != user_id or token_role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        return ServiceService.delete_service(service_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
