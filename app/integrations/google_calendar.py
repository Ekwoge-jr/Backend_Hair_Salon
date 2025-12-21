from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timezone
import os
import json
from app.models.orm.user_model import UserModel
from app.models.repositories.user_repo import UserRepository
from app import db


# Google Calendar API Scopes (defines what you can access)
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

# Path to token.json (stores access/refresh tokens)
# TOKEN_FILE = "token.json"
# CREDENTIALS_FILE = "/Users/mrfomfoh/Downloads/Backend_Hair_Salon-main/credentials.json"
CREDENTIALS_FILE = "/Users/mrfomfoh/Documents/Inch Tech/Projects/application/hs-backend/credentials.json"
# Changed the above credential file location



# Helper - read client_id/secret from credentials.json so we can build refreshable Credentials later
def _read_client_info():
    with open(CREDENTIALS_FILE, "r") as f:
        data = json.load(f)
    client_info = data.get("web")
    return client_info

def build_flow(redirect_uri):
    """Create a Flow for server-side (web) OAuth flow"""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow

def save_tokens_for_user(email: str, creds: Credentials):
    """Save tokens and expiry to the database for a given user"""
    # user = UserRepository.get_users_by_email(email)

    user = db.session.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        raise RuntimeError("User not found")
    
    user.google_access_token = creds.token
    user.google_refresh_token = creds.refresh_token
    # ensure expiry is timezone-aware UTC datetime

    print(user.google_access_token)

    print(user.google_refresh_token)

    if creds.expiry:
        user.google_token_expiry = creds.expiry.astimezone(timezone.utc).replace(tzinfo=None)
        # we store naive UTC datetime - be consistent in comparisons
    db.session.commit()
    
    print(f"--- Database updated successfully for {email} ---")


def get_calendar_service_for_user(email: str):
    """Return googleapiclient service for this user, refreshing tokens if needed."""

    user = UserRepository.get_users_by_email(email)

    

    if not user:
        raise RuntimeError("User not found")

    if not (user.google_access_token or user.google_refresh_token):
        print(" Stylist email: ", email)
        print(" Stylist access: ", user.google_access_token)
        print(" Stylist refresh: ", user.google_refresh_token)

        raise RuntimeError("No Google tokens for this user.")

    

    client_info = _read_client_info()
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri=client_info.get("token_uri") or "https://oauth2.googleapis.com/token",
        client_id=client_info.get("client_id"),
        client_secret=client_info.get("client_secret"),
        scopes=SCOPES
    )

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_tokens_for_user(user.email, creds)

    # Build service
    service = build("calendar", "v3", credentials=creds)
    return service













"""  
def get_token_file(email):
    safe_email = email.replace("@", "_").replace(".", "_")
    return f"tokens/{safe_email}_token.json"


def get_calendar_service(user_email):
    os.makedirs("tokens", exist_ok=True)  ## ensure folder exists first

    token_file = get_token_file(user_email)
    creds = None


    # Load saved credentials if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If no valid credentials, prompt login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8085) # added, changed from 8080 to 8085
        
        # Save the credentials for that specific email
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)
"""

    
def create_google_event(summary, description, start_time, end_time, user_email,       stylist_email):
    """
    Creates a Google Calendar event and returns the event ID.
    """
    service = get_calendar_service_for_user(stylist_email)
    # TIMEZONE = str(get_localzone()) # Detect system timezone automatically

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time,
        },
        "end": {
            "dateTime": end_time,
        },
        "attendees": [
            {"email": user_email}
        ]
    }

    created_event = service.events().insert(calendarId="primary", body=event, sendUpdates="all" ).execute()
    return created_event.get("id")


def cancel_google_event(event_id, user_email):
    """
    Cancles a Google Calendar event.
    """
    service = get_calendar_service_for_user(user_email)
    try:
        # this line of code deletes the event from google
        service.events().delete(calendarId="primary", eventId=event_id).execute()

        # while this event just sets the status to cancelled, but users can still see it dimmed in their calendar
        #service.events().patch(calendarId="primary", eventId=event_id, body={'status': 'cancelled'}).execute()
        return {"message": "Event cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}
        
    