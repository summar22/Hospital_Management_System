from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def create_event(token_data, title, date, start_time, end_time, description=''):
    """
    Create a Google Calendar event using OAuth2 token.
    
    Args:
        token_data: Dictionary containing OAuth2 token information
        title: Event title
        date: Date object
        start_time: Time object
        end_time: Time object
        description: Event description
    """
    # Check if this is a demo/mock token
    if token_data.get('is_mock'):
        print(f"\n[DEMO CALENDAR] Mock Event Created Successfully:")
        print(f"  Title: {title}")
        print(f"  Date/Time: {date} ({start_time} to {end_time})")
        print(f"  Description: {description}\n")
        return {
            'htmlLink': 'https://calendar.google.com/calendar/r/event/mock-demo-id',
            'summary': title,
            'is_mock': True
        }

    # Create credentials from token data
    credentials = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/calendar'])
    )
    
    # Refresh token if expired
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    
    # Build the Calendar service
    service = build('calendar', 'v3', credentials=credentials)
    
    # Create event datetime strings
    start_datetime = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': True,
        },
    }
    
    # Insert the event
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')
    
    return event
