# flake8: noqa
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json
import requests
from datetime import datetime


api_key = os.getenv("GEMINI_API_KEY");
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#TOOLS -----------------------
#e.g. read_from_db , insert_into_db etc.
def get_weather(city: str):
    #we can call here API to get the weather
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error fetching weather data for {city}"
    
    return "The weather in " + city + " is " + response.text

def run_command(cmd: str):
    result = os.system(cmd)
    return result

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}


#so bsically make the various tools and make a framework to call the tools based on the user query
#-----------------------------------


SYSTEM_PROMPT = """
You are a helpful AI assistent
You work on start,plan,action,observer,resolve mode

for the user input and available tools, you will plan the step-by-step execution and select the relevant tool from availabe tools.
and based on tool selection ,you will perform the action to call the tool.
wait for the observation and based on the observation from the tool , you will resolve the user query.

Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.


Example: 
Input: "Whats the weather today in Mumbai?"
Output: {{step:"plan","content":"The User is interested in the weather of Mumbai.From the available Tools, I will use the get_weather tool to fetch the current weather for Mumbai."}}
Output:{{step:"action","function":"get_weather","input":"Mumbai"}}
Output:{{step:"observe","output":"42 degree celsius"}}
Output:{{step:"resolve","content":"The current weather in Mumbai is 42 degree celsius"}}


Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]
while True:
    query = input("Enter your query: ")
    messages.append({"role": "user", "content": query})

    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type": "json_object"},
            messages=messages
        )
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":
            print(" 🧠:",parsed_response.get("content"))
            continue
        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print("🔧:", f"Executing tool '{tool_name}' with input '{tool_input}'")

            if tool_name in available_tools:
                tool_output = available_tools[tool_name](tool_input)
                messages.append({"role": "assistant", "content": ""})
                continue
            
        if parsed_response.get("step") == "resolve":
            print("✅:", parsed_response.get("content"))
            break
    