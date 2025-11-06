from flask import Blueprint, request, jsonify
from app import db
from app.services.service_service import ServiceService
from werkzeug.utils import secure_filename
from datetime import datetime
import os


service_bp = Blueprint("service_bp", __name__)


UPLOAD_FOLDER = "app/uploads/services"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Make sure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@service_bp.route("/create-service", methods= ["POST"])
def create_service():

    """
    Create a new service
    ---
    tags:
      - Services
    description: Uploads a service image and saves the service details in the database.
    consumes:
      - multipart/form-data
    parameters:
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
    """


    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    image = request.files.get("image")
    duration = request.form.get("duration")

    if not all([name, description, price, image]):
        return jsonify({"error": "All fields are required"}), 400
    
    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid image format"}), 400
    
    filename = secure_filename(image.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)

    try:
        result=  ServiceService.create_service(name, description, price, filename, duration)
        return jsonify(result.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    



@service_bp.route("/update/<int:service_id>", methods=["PUT"])
def update(service_id):

    """
    Update a service
    ---
    tags:
      - Services
    description: Updates an existing service and optionally replaces its image.
    consumes:
      - multipart/form-data
    parameters:
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
        return jsonify(results), 200
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



@service_bp.route("/delete/<int:service_id>", methods=["DELETE"])
def delete_service(service_id):

    """
    Delete a service
    ---
    tags:
      - Services
    parameters:
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
    try:
        return ServiceService.delete_service(service_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
