from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os


# Google Calendar API Scopes (defines what you can access)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Path to token.json (stores access/refresh tokens)
# TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "/Users/mrfomfoh/Downloads/Backend_Hair_Salon-main/credentials.json"


def get_token_file(email):
    safe_email = email.replace("@", "_").replace(".", "_")
    return f"tokens/{safe_email}_token.json"


def get_calendar_service(user_email):
    creds = None

    token_file = get_token_file(user_email)

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
        os.makedirs("tokens", exist_ok=True)
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_google_event(summary, description, start_time, end_time, user_email):
    """
    Creates a Google Calendar event and returns the event ID.
    """
    service = get_calendar_service(user_email)
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
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event.get("id")


def cancel_google_event(event_id):
    """
    Cancles a Google Calendar event.
    """
    service = get_calendar_service()
    try:
        # this line of code deletes the event from google
        service.events().delete(calendarId="primary", eventId=event_id).execute()

        # while this event just sets the status to cancelled, but users can still see it dimmed in their calendar
        #service.events().patch(calendarId="primary", eventId=event_id, body={'status': 'cancelled'}).execute()
        return {"message": "Event cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}
        
    