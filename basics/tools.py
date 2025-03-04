import json
import os

import requests
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# define function that we want to call
def get_weather(latitude, longitude):
    """This is a publicly available API that returns the weather for a given location"""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]

# Step 1: call model with get_weather tool defined
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "You are a helpful weather assistant"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the weather in Singapore today?"}
]

completion = client.chat.completions.create(
    model = "gpt-4o",
    messages=messages,
    tools=tools
)

# Step 2: model decides to call function
print(completion.model_dump())

# Step 3: Execute get weather function

# **args is used to unpack a dictionary into named function arguments.
# It converts {"key": "value"} into key="value" argument pairs.
# It avoids manually extracting dictionary values before calling functions.

def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args) 
    
for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)

    result = call_function(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )

# Step 4: Supply result and call model again
class weatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celcius for the given location"
    )
    response: str = Field(
        description="A natural language response to the user's question"
    )

completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    response_format=weatherResponse
)

# Step 5: check model response
final_response = completion_2.choices[0].message.parsed
final_response.temperature
final_response.response

print(final_response)
    

