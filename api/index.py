from fastapi import FastAPI, Query
from openai import OpenAI
import requests
import json
from dotenv import load_dotenv
import os
import re 
from pydantic import BaseModel

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

@app.get("/api/py/search_perplexity")
def search_perplexity(
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
    
    


def format_recommendations(recommendations_text: str, citations: list) -> str:
    """
    Process the recommendations text to:
      1. Split the text into separate recommendation blocks.
      2. For each block, find citation markers like [1][2][5].
      3. Remove the markers from the recommendation text.
      4. Look up each citation number (using 1-indexing) in the citations list.
      5. Append a "Relevant Link:" section with the corresponding links.
      
    Returns the final formatted string.
    """
    # Split by double newlines (assuming each recommendation is separated by blank lines)
    blocks = re.split(r'\n\s*\n', recommendations_text.strip())
    formatted_blocks = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Find all citation markers (e.g., [1], [2], etc.)
        marker_matches = re.findall(r'\[(\d+)\]', block)
        # Convert marker strings to integers (assuming markers are 1-indexed)
        marker_indices = [int(num) for num in marker_matches]

        # Retrieve the corresponding links from the citations list.
        links = []
        for idx in marker_indices:
            if 1 <= idx <= len(citations):
                links.append(citations[idx - 1])
        # Deduplicate links while preserving order.
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                unique_links.append(link)
                seen.add(link)
                
        # Remove the citation markers from the block.
        clean_block = re.sub(r'\[\d+\]', '', block).strip()
        
        # Extract a leading number (if any) and format the output.
        match = re.match(r'^(\d+)\.\s*(.*)$', clean_block)
        if match:
            num = match.group(1)
            text_content = match.group(2)
            formatted_block = (
                f"{num}. Recommendation: \"{text_content}\" "
                f"Relevant Link: [{', '.join(unique_links)}]"
            )
        else:
            formatted_block = (
                f"Recommendation: \"{clean_block}\" "
                f"Relevant Link: [{', '.join(unique_links)}]"
            )
        
        formatted_blocks.append(formatted_block)
    
    return "\n\n".join(formatted_blocks)

@app.post("/api/py/passive_recommendations")
def passive_recommendations():
    # A combined JSON string that represents responses from Google Calendar and Google Mail APIs.
    combined_text = '''
[
  {
    "from": "Gamer <gamer@videogames.com>",
    "subject": "Call of Duty is the Best!",
    "snippet": "I absolutely love playing Call of Duty.",
    "text": "Hi there,\\n\\nI just wanted to say that Call of Duty is my absolute favorite game. The action, the strategy, and the adrenaline rush are unparalleled. Can’t wait for the next update!\\n\\nBest,\\nGamer",
    "html": "<p>Hi there,</p><p>I just wanted to say that <strong>Call of Duty</strong> is my absolute favorite game. The action, the strategy, and the adrenaline rush are unparalleled. Can’t wait for the next update!</p><p>Best,<br/>Gamer</p>",
    "html-parsed": "Hi there, I just wanted to say that Call of Duty is my absolute favorite game. The action, the strategy, and the adrenaline rush are unparalleled. Can’t wait for the next update! Best, Gamer"
  },
  {
    "from": "Traveler <traveler@example.com>",
    "subject": "New Mexico Adventure",
    "snippet": "I'm planning a trip to New Mexico soon!",
    "text": "Dear friend,\\n\\nI've been dreaming about a trip to New Mexico for ages. The landscape, the culture, and the open roads call to me. I would love some suggestions on must-see spots!\\n\\nCheers,\\nTraveler",
    "html": "<p>Dear friend,</p><p>I've been dreaming about a trip to <strong>New Mexico</strong> for ages. The landscape, the culture, and the open roads call to me. I would love some suggestions on must-see spots!</p><p>Cheers,<br/>Traveler</p>",
    "html-parsed": "Dear friend, I've been dreaming about a trip to New Mexico for ages. The landscape, the culture, and the open roads call to me. I would love some suggestions on must-see spots! Cheers, Traveler"
  },
  {
    "from": "Foodie <foodie@tastymeals.com>",
    "subject": "Biriyani Bliss",
    "snippet": "I just love biriyani so much!",
    "text": "Hello,\\n\\nI must share how much I adore biriyani. The blend of spices, tender meat, and fragrant rice is a culinary masterpiece. Every bite is an adventure!\\n\\nWarm regards,\\nFoodie",
    "html": "<p>Hello,</p><p>I must share how much I adore <em>biriyani</em>. The blend of spices, tender meat, and fragrant rice is a culinary masterpiece. Every bite is an adventure!</p><p>Warm regards,<br/>Foodie</p>",
    "html-parsed": "Hello, I must share how much I adore biriyani. The blend of spices, tender meat, and fragrant rice is a culinary masterpiece. Every bite is an adventure! Warm regards, Foodie"
  },
  {
    "from": "FitnessSeeker <fitseek@health.com>",
    "subject": "Looking for Affordable Gyms",
    "snippet": "I need some recommendations for affordable gyms.",
    "text": "Hi,\\n\\nI'm on the lookout for affordable gyms in my area. If you have any recommendations or insights into places that offer good facilities without breaking the bank, please let me know.\\n\\nThanks,\\nFitnessSeeker",
    "html": "<p>Hi,</p><p>I'm on the lookout for affordable gyms in my area. If you have any recommendations or insights into places that offer good facilities without breaking the bank, please let me know.</p><p>Thanks,<br/>FitnessSeeker</p>",
    "html-parsed": "Hi, I'm on the lookout for affordable gyms in my area. If you have any recommendations or insights into places that offer good facilities without breaking the bank, please let me know. Thanks, FitnessSeeker"
  },
  {
    "from": "HungryJohn <john@foodfinder.com>",
    "subject": "Looking for Cheap Chicken Nearby",
    "snippet": "I need help finding some cheap chicken options nearby.",
    "text": "Hey there,\\n\\nI'm on a budget and looking for some cheap chicken options in the vicinity. Could you please help me find a good place to grab a meal? Your suggestions would be greatly appreciated.\\n\\nBest,\\nHungryJohn",
    "html": "<p>Hey there,</p><p>I'm on a budget and looking for some cheap chicken options in the vicinity. Could you please help me find a good place to grab a meal? Your suggestions would be greatly appreciated.</p><p>Best,<br/>HungryJohn</p>",
    "html-parsed": "Hey there, I'm on a budget and looking for some cheap chicken options in the vicinity. Could you please help me find a good place to grab a meal? Your suggestions would be greatly appreciated. Best, HungryJohn"
  }
]
    '''
    # Define the instructions for the LLM.
    instructions = (
        "Using the above Google Calendar and Google Mail API responses, analyze the user's information to identify meaningful context about their interests, plans, and lifestyle. "
        "Then provide recommendations to enhance their life."
        "Below are some examples BUT DONT BE LIMITED TO THEM, ESSENTIALLY IMAGINE YOU ARE AN ASSISTANT AND SHARE INFORAMTION/RECOMENDATIONS THAT MAY BE USEFUL"
        "- If the user likes the video game 'Elden Rings', recommend similar games.\n"
        "- If the user likes food, recommend good restaurants or food places in Montreal.\n"
        "- If the user mentioned they want to go skiing, recommend top skiing locations with their prices.\n"
        "- If the user mentioned they want to visit Dubai, recommend the cheapest flights from Montreal to Dubai with prices.\n"
        "- If the user has a calendar event for today, check the weather and advise accordingly.\n\n"
        "Provide exactly 4 outputs in list format as follows:\n"
        "1. Here's some top restaurants: 1.KFC 2.BFC 3.Burger King with their link\n"
        "2. Cheapest flight to dubai\n"
        "3. Games you may also like: RDR2, Halo Guardians\n"
        "4. It may rain today, do take your umbrella\n"
        "Don't recoment the same type of recomendation twice!" 
        "Do not include any additional text."
    )
    
    full_prompt = f"{combined_text}\n\n{instructions}"
    
    # Call the Perplexity API (using the sonar-pro model).
    client = OpenAI(
        api_key=os.environ["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai"
    )
    response = client.chat.completions.create(
         model="sonar-pro",
         messages=[{"role": "user", "content": full_prompt}],
    )
    
    # Extract the recommendations text.
    recommendations_text = response.choices[0].message.content
    
    
    # Attempt to extract the citations list from the response.
    citations = []
    if hasattr(response, "citations"):
        citations = response.citations
    elif isinstance(response, dict) and "citations" in response:
        citations = response["citations"]
    # (If no citations are provided, citations will remain an empty list.)
    
    # Format the recommendations by replacing citation markers with the actual links.
    formatted_recommendations = format_recommendations(recommendations_text, citations)
    
    return {"recommendations": formatted_recommendations}