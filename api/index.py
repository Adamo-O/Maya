from fastapi import FastAPI
# import openai
# import requests

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/test")
def hello_fast_api():
    return {"message": "test"}

@app.get("/api/py/create_calendar_event")
def create_calendar_event():
    # Generate google calendar link
    # Format date in yyyyMMdd'T'HHmmSS
    startDate = "20220606'T'213000"
    endDate = "20220606'T'223000"
    baseLink = "https://calendar.google.com/calendar/render"
    config = {
        "action": "TEMPLATE",
        "text": "X restaurant opens",
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


# ! Code to generate Google Calendar Link, have to convert to Python
#   const formatDateGoogleCalendar = (date: Date) => {
#     return format(date, "yyyyMMdd'T'HHmmSS");
#   };

#   const getGoogleCalendarLink = () => {
#     const baseLink = "https://calendar.google.com/calendar/render";

#     const config = {
#       action: "TEMPLATE",
#       text: tournament.name,
#       dates: `${formatDateGoogleCalendar(tournament.startDate)}/${
#         tournament.endDate
#           ? formatDateGoogleCalendar(tournament.endDate)
#           : formatDateGoogleCalendar(
#               addHours(new Date(tournament.startDate), 1),
#             )
#       }`,
#       location: tournament.address,
#       details: tournament.descriptionText ?? undefined,
#     };

#     const params = new URLSearchParams(config as Record<string, string>);

#     return `${baseLink}?${params.toString()}`;
#   };
