import os

from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# define response format in pydantic model
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

# call the model
completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content"
         : "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    response_format=CalendarEvent,
)

# parse the response
event = completion.choices[0].message.parsed
event.name
event.date
event.participants

print(event)