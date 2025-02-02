from fastapi import FastAPI
from openai import OpenAI
import requests
import json
from dotenv import load_dotenv
import os
from api.integrations import get_gmail_service, get_n_latest_emails, find_events_on_day, get_calendar_service
from pydantic import BaseModel

load_dotenv()
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

class Email(BaseModel):
    subject: str
    from_email: str
    text: str

@app.post("/api/py/main")
def main_route(email: Email):
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    # Create a mock ChatGPT prompt
    prompt = """You are a personal assistant tasked with filtering out emails that are actionable to the user. 
    Such emails could be:
    - Meeting requests
    - Emails that require a response
    - Travel or trip information
    - Event details
    - Shopping lists sent by humans
    - Links sent by humans and are not promotional
    Emails of similar content should also be considered.
    Some emails that should be ignored are:
    - Emails that are promotional or are marketing emails
    - Order confirmations
    - Ads
    - Emails where there is no obvious action to be taken
    With this email context in triple backticks, if you believe that the email is work taking action on, give at most three distinct actions that a user can do. 
    If the email is an ad or a confirmation, it is not worth answering. 
    If the email is suggesting an action that requires going to a website, consider linking to the mentioned site with some query parameters that can help with the search. 
    Only show the actions, do not give more context.
    Make sure each action contains a link to click on and is less than 6 words. 
    If you are making a reply, make a mailto link as a reply with some appropriate content in the body. Make sure to use the %20 escape character for spaces.
    If a time and/or date is mentioned, make one of the tasks mention the time and link to google calendar. All times are in Eastern Standard Time make sure to convert to UTC time before making the link.
    Format the actions as follows <action> - <link>. Do not format the link: 
    """
        
    email = f"""
    Subject: {email.subject}
    From: {email.from_email}
    
    {email.text}
    """
    
    message = f"{prompt}\n```\n{email}\n```"
    
    tools = [{
        "type": "function",
        "function": {
            "name": "process_actions",
            "description": "Process the actions extracted from the email",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "link": {"type": "string"},
                            }
                        },
                        "required": ["action", "link"]
                    }
                }
            }
        }
    }]
    
    # Use ChatGPT to process the user's request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        tools=tools,
    )
    
    print(response.choices[0].message)
    
    # Extract the function call details
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    
    result = process_actions(args['title'], args['actions'])
    return result

def process_actions(title: str, actions: list):
    # Process the actions
    print(title, actions)
    
    # For each action that has a google calendar link, check if the user is available
    for action in actions:
        if "google.com/calendar" in action["link"]:
            # Check user's calendar to see if they are available
            calendar_service = get_calendar_service()
            
            # Extract the date from the link
            date = action["link"].split("dates=")[1].split("/")[0]
            
            # Extract day, month, year from date
            year = int(date[:4])
            month = int(date[4:6])
            day = int(date[6:8])
            events = find_events_on_day(calendar_service, day, month, year)
            
            # Available, use calendar event link as is
            if not events:
                continue
            
            # Not available, suggest a reply to the email AND suggest a link to day view of calendar
            # TODO FINISH
    
    # TODO Check user's calendar to see if they are available
    
    # If available, suggest calendar event link
    # If not available, suggest a reply to the email AND suggest a calendar event link

    
    return {"title": title, "actions": actions}


@app.get("/api/py/test")
def openai_test():
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    # Create a mock ChatGPT prompt
    prompt = "Add a calendar event for the day X restaurant opens on June 6th"
    
    # Define the function for ChatGPT to use
    tools = [{
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a new event in Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "date": {"type": "string", "format": "date"}
                },
                "required": ["title", "date"]
            }
        }
    }]
    
    # Use ChatGPT to process the user's request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
    )
    
    print(response)
    # Extract the function call details
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    
    result = create_calendar_event(args['title'], args['date']) 
    return result

# @app.get("/api/py/create_calendar_event")
def create_calendar_event(title: str, date: str):
    # Generate google calendar link
    # Format date in yyyyMMdd'T'HHmmSS
    startDate = "20220606'T'213000"
    endDate = "20220606'T'223000"
    baseLink = "https://calendar.google.com/calendar/render"
    config = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{startDate}/{endDate}",
        "location": "X restaurant",
        "details": "X restaurant opens on June 6th",
    }
    params = "&".join([f"{key}={value}" for key, value in config.items()])
    google_calendar_link = f"{baseLink}?{params}"
    return {"google_calendar_link": google_calendar_link}


@app.get("/api/py/get_n_newest_emails")
def get_n_newest_emails(n: int = 10):
    gmail_service = get_gmail_service()
    emails = get_n_latest_emails(gmail_service, n)
    return emails

# def create_calendar_event(title, date):
#     # Make API call to your backend service
#     response = requests.post('https://your-backend-service.com/create-event', 
#                              json={'title': title, 'date': date})
#     return response.json()

# # Define the function for ChatGPT to use
# functions = [
#     {
#         "name": "create_calendar_event",
#         "description": "Create a new event in Google Calendar",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "title": {"type": "string"},
#                 "date": {"type": "string", "format": "date"}
#             },
#             "required": ["title", "date"]
#         }
#     }
# ]

# # Use ChatGPT to process the user's request
# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo-0613",
#     messages=[{"role": "user", "content": "Add a calendar event for the day X restaurant opens on June 6th"}],
#     functions=functions,
#     function_call="auto"
# )

# # Extract the function call details
# function_call = response['choices'][0]['message']['function_call']
# if function_call['name'] == 'create_calendar_event':
#     args = json.loads(function_call['arguments'])
#     result = create_calendar_event(args['title'], args['date'])
#     print(result)