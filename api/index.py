from fastapi import FastAPI, Query
from openai import OpenAI
import requests
import json
from dotenv import load_dotenv
import os
import re 

load_dotenv()
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/main")
def openai_test():
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    # Create a mock ChatGPT prompt
    prompt = """With this email context in triple backticks, if you believe that the email is work taking action on, give at most three distinct actions that a user can do. 
        If the email is an ad or a confirmation, it is not worth answering. DO NOT GIVE ACTIONS IF THERE ARE NO VALID ANSWERS
        Only show the actions, do not give more context.
        Make sure each action contains a link to click on and is less than 6 words. 
        If you are making a reply, make a mailto link as a reply with some appropriate content in the body. Make sure to use the `%20` escape character for spaces.
        If a time and/or date is mentioned, make one of the tasks mention the time and link to google calendar. All times are in Eastern Standard Time make sure to convert to UTC time before making the link.
        Format the actions as follows <action> - <link>. Do not format the link.
        """
        
    email = """
    Subject: Re: hello
    From: mayaappemail@gmail.com
    Do you want to meet tomorrow at 5 pm at my place?

    On Sat, Feb 1, 2025 at 6:58 PM Maya <mayaappemail@gmail.com> wrote:

    > hiiii
    >
    > On Sat, Feb 1, 2025 at 6:57 PM Koosha Gholipour <
    > koosha.gholipour@gmail.com> wrote:
    >
    >> hi
    >>
    >
    """
    
    message = f"{prompt}\n```\n{email}\n```"
    
    # TODO Check user's calendar to see if they are available
    # If available, suggest calendar event link
    # If not available, suggest a reply to the email AND suggest a calendar event link
    tools = [{
        "type": "function",
        "function": {
            "name": "process_actions",
            "description": "Process the actions extracted from the email",
            "parameters": {
                "type": "object",
                "properties": {
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
    
    result = process_actions(args['actions'])
    return result

def process_actions(actions):
    # Process the actions
    print(actions)
    return actions


# @app.get("/api/py/test")
# def openai_test():
#     client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
#     # Create a mock ChatGPT prompt
#     prompt = "Add a calendar event for the day X restaurant opens on June 6th"
    
#     # Define the function for ChatGPT to use
#     tools = [{
#         "type": "function",
#         "function": {
#             "name": "create_calendar_event",
#             "description": "Create a new event in Google Calendar",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "title": {"type": "string"},
#                     "date": {"type": "string", "format": "date"}
#                 },
#                 "required": ["title", "date"]
#             }
#         }
#     }]
    
#     # Use ChatGPT to process the user's request
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#         tools=tools,
#     )
    
#     print(response)
#     # Extract the function call details
#     tool_call = response.choices[0].message.tool_calls[0]
#     args = json.loads(tool_call.function.arguments)
    
#     result = create_calendar_event(args['title'], args['date']) 
#     return result

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

@app.get("/api/py/multi_task")
def multi_task(
    prompt: str = Query(
        "Remind me to buy eggs on Miley Cyrus's birthday", 
        description="Your natural language prompt describing the reminder or appointment."
    )
):
    """
    It'll take a natural language prompt (like fr example:
      "Remind me to buy milk two weeks later" or "Book appointment coming Saturday")
    and appends an instruction that forces the model to reply in JSON format containing
    exactly two keys: 'title' and 'date' (in YYYY-MM-DD format). The extracted values are then
    passed to the calendar event creation function.
    """
    # Setting up perplexity 
    client = OpenAI(
        api_key=os.environ["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai"
    )
    
    # fking with instruction to force JSON output.
    instructions = (
        "Please reply with a JSON object containing exactly two keys: "
        "'title' and 'date'. The 'title' should be a brief description extracted from the above prompt, "
        "and 'date' should be the absolute date in YYYY-MM-DD format computed from any relative expressions. "
        "Do not include any additional text."
    )
    
    conversation = f"{prompt}. {instructions}"
    
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[{"role": "user", "content": conversation}],
    )
    
    # Extract the response content.
   
    response_dict = response.to_dict() if hasattr(response, "to_dict") else response

    content = response_dict["choices"][0]["message"]["content"]
    
    # try to parse the output as JSON.
    try:
        data = json.loads(content)
        title = data.get("title", prompt)
        date = data.get("date", "")
    except Exception as e:
        # Fallback: try to extract a date using regex and use the prompt as title.
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", content)
        date = date_match.group(1) if date_match else ""
        title = prompt
    
    if date:
        # print(title,date)
        # return None
        return create_calendar_event(title, date)
    else:
        return {"message": "Could not extract a valid date from the response.", "raw_response": content}