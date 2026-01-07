from flask import Blueprint, redirect, request, jsonify, session, url_for
from app.models.repositories.user_repo import UserRepository
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity  
from app import bcrypt, db



from app.models.orm.user_model import UserModel

from app.integrations.google_calendar import build_flow, save_tokens_for_user
import os


# Allow libraries to use http for OAuth in local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



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


      response = {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
      }

      #Printing
      print("Google testing")

      # ✅ Check if stylist needs Google authentication
      if user.role == "stylist" and user.google_refresh_token is None:
          response["google_auth_required"] = True
          response["google_auth_url"] = url_for("auth_bp.google_login", _external=True)
          print("Google Testing works")

      else:
          response["google_auth_required"] = False
          print("Google Testing doesn't work")

      return jsonify(response), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # user_id = get_jwt_identity()
    # new_access = create_access_token(identity=user_id)
    # return {"access_token": new_access}
    current_identity = get_jwt_identity() 
    new_access = create_access_token(identity=current_identity)
    return jsonify({"access_token": new_access}), 200





# Start Google OAuth flow. The frontend must call this with the Authorization: Bearer <access_token> header
@auth_bp.route("/google/login")
@jwt_required()
def google_login():
    identity = get_jwt_identity()
    user_id = identity["id"]
    # redirect uri must match one registered in Google Console
    redirect_uri = url_for("auth_bp.google_callback", _external=True)
    print("**************** Redirected to google !!!!!!!!!!!!!!!!!!!")
    flow = build_flow(redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type="offline",   # get refresh token

        include_granted_scopes="false", # Added this to prevent merging old scopes
        
        prompt="consent"
    )
    # You can return the URL to the frontend (they open in browser)
    return jsonify({"auth_url": authorization_url}), 200


# Google will redirect here; frontend should forward the callback URL including querystring to this endpoint,
# and the request must include Authorization header with stylist JWT so we can link tokens to the logged-in stylist.
@auth_bp.route("/google/callback")
#@jwt_required()
def google_callback():
    # Important: frontend must call this endpoint with the full callback URL (including ?code=...&state=...)
    # For ease, have the frontend take the request URL string (window.location.href) and POST it to backend.
    # identity = get_jwt_identity()
    # user = UserRepository.get_users_by_id(identity["id"])
    
    # The frontend should send the 'full_url' param containing the Google's redirect URL including code & state
    full_url = request.args.get("full_url") or request.headers.get("X-Original-Url") or request.url
    # Build flow and fetch tokens
    redirect_uri = url_for("auth_bp.google_callback", _external=True)
    flow = build_flow(redirect_uri)
    # `fetch_token` expects full authorization_response URL (with code & state)
    flow.fetch_token(authorization_response=full_url)
    creds = flow.credentials



    # 2. Get the email from the Google Token to identify the user
    # This replaces get_jwt_identity()
    user_info_service = flow.authorized_session().get('https://www.googleapis.com/oauth2/v3/userinfo')
    user_info = user_info_service.json()
    email = user_info.get("email")

    if not email:
        return jsonify({"error": "Failed to get user info from Google", "debug": user_info}), 400

    
    # Save tokens in DB for the stylist
    print("######## About to save to database *******************")
    save_tokens_for_user(email, creds)
    print("Saved to database !!!!!!!!!!!!!!!!!!!!!!!!!!")

  
    # return jsonify({"message": "Google connected successfully"}), 200
    FRONTEND_DASHBOARD_URL = "https://kc-afrobraids.inchtechs.com/stylist/dashboard?google_auth=success" # Adjust this to your actual route
    return redirect(FRONTEND_DASHBOARD_URL, code=302) # Use a 302 redirect

















"""
from google_auth_oauthlib.flow import Flow
import os

@auth_bp.route('/google/login')
@jwt_required()
def google_login():

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE = "D:\FET\Internship\Hair Salon project\Backend\credentials.json",
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri=url_for('auth_bp.google_callback', _external=True)
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    session['state'] = state
    return redirect(authorization_url)




@auth_bp.route('/google/callback')
@jwt_required()
def google_callback():

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE = "D:\FET\Internship\Hair Salon project\Backend\credentials.json" ,
        scopes=["https://www.googleapis.com/auth/calendar"],
        state=session['state'],
        redirect_uri=url_for('auth_bp.google_callback', _external=True)
    )

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    user_identity = get_jwt_identity()

    user = UserRepository.get_user_by_id(user_identity["id"])

    user.google_access_token = credentials.token
    user.google_refresh_token = credentials.refresh_token
    user.google_token_expiry = credentials.expiry

    db.session.commit()

    return jsonify({"message": "Google Calendar connected successfully ✅"})

"""