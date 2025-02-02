import os.path
import base64
from bs4 import BeautifulSoup
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/calendar.readonly"]

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)
  
  
# Example usage:
# Call the Gmail API
# gmail_api_service = get_gmail_service()
# emails = get_n_latest_emails(gmail_api_service, n=10)
# for email in emails:
#     print(f"Subject: {email['subject']}")
#     print(f"From: {email['from']}")
#     if "text" in email:
#         print(email["text"])
#     elif "html-parsed" in email:
#         print(email["html-parsed"])
#     elif "html" in email:
#         print(email["html"])
#     else:
#         print("No text or html content found")
#     print("\n")
                   
def get_n_latest_emails(service, n = 10, query = ["category:primary", "label:unread"]):
    query_string = " ".join(query)
    results = service.users().messages().list(userId='me', q=query_string, maxResults=n).execute()
    email_ids = results.get("messages", [])
    
    if not email_ids:
      print("No emails found.")
      return []
    else:
        emails = []
        for message_id in email_ids:
            data = {}
            email_ = service.users().messages().get(userId="me", id=message_id["id"]).execute()
            data["id"] = email_["id"]
            data["snippet"] = email_["snippet"]
            data["subject"] = list(filter(lambda headers: headers['name'] == "Subject", email_["payload"]["headers"]))[0]["value"]
            data["from"] = list(filter(lambda headers: headers['name'] == "From", email_["payload"]["headers"]))[0]["value"]
            if "parts" in email_["payload"]:
                for parts in email_["payload"]["parts"]:
                    if "text/plain" in parts["mimeType"] and parts["body"]["size"] > 0:
                        b64string = parts["body"]["data"]
                        string = base64.urlsafe_b64decode(b64string + "===").decode("utf-8")
                        data["text"] = string
                    elif "text/html" in parts["mimeType"]:
                        b64string = parts["body"]["data"]
                        html = base64.urlsafe_b64decode(b64string + "===").decode("utf-8")
                        parsed = (BeautifulSoup(html, 'html.parser').text)
                        lessed = " ".join(parsed.split())
                        data["html"] = html
                        data["html-parsed"] = lessed
            else:
                # there is no multipart, figure out if just text or html
                if "text/plain" in email_["payload"]["mimeType"]:
                    b64string = email_["payload"]["body"]["data"]
                    string = base64.urlsafe_b64decode(b64string + "===").decode("utf-8")
                    data["text"] = string
                elif "text/html" in email_["payload"]["mimeType"]:
                    b64string = email_["payload"]["body"]["data"]
                    html = base64.urlsafe_b64decode(b64string + "===").decode("utf-8")
                    parsed = (BeautifulSoup(html, 'html.parser').text)
                    lessed = " ".join(parsed.split())
                    data["html"] = html
                    data["html-parsed"] = lessed
            if "text" not in data and "html" not in data:
                # look, if the email is this hard to read, it's probably not important
                continue
            emails.append(data)
                
        return emails
    
    
# Example usage:
# calendar_service = get_calendar_service()
# now = datetime.datetime.now(datetime.timezone.utc).isoformat()
# today = datetime.datetime.now().day

# events = find_events_on_day(calendar_service, today, 3, 2022)
# if not events:
#     print("No upcoming events found.")
# for event in events:
#     start = event["start"].get("dateTime")
#     end = event["end"].get("dateTime")
#     timezone = event["start"].get("timeZone")
#     title = event["summary"]
#     link = event.get("htmlLink")
#     print(start, end, event["summary"])
#     print(link)

def find_events_on_day(service, day, month, year, tz=datetime.timezone.utc):
    date = datetime.datetime(year, month, day, tzinfo=tz)
    start = date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end = date.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events

def find_next_n_events(service, n=10):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=n,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events

def find_events_between_dates(service, start_date, end_date):
    start = start_date.isoformat()
    end = end_date.isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events