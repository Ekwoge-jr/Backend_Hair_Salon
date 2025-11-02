from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os


# Google Calendar API Scopes (defines what you can access)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Path to token.json (stores access/refresh tokens)
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "D:\FET\Internship\Hair Salon project\Backend\credentials.json"

def get_calendar_service():
    creds = None

    # Load saved credentials if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, prompt login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for next time
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_google_event(summary, description, start_time, end_time):
    """
    Creates a Google Calendar event and returns the event ID.
    """
    service = get_calendar_service()
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
        
    