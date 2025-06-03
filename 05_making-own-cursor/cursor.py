from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json
import requests
from datetime import datetime
import subprocess

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_weather(city:str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error fetching weather data for {city}"
    return "The weather in " + city + " is " + response.text

def run_command(cmd: str):
    result = os.system(cmd)
    return result
    
def write_file(filepath:str, content:str):
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        return f"File '{filepath}' written successfully."
    except Exception as e:
        return f"Error writing to file: {str(e)}"


available_tools = {
    "get_weather":get_weather,
    "run_command":run_command,
    "write_command":write_file
}

SYSTEM_PROMPT = '''
You are a senior AI Code Assistant named "Coder Pro", an advanced autonomous system with 20+ years of deep experience in building,
debugging, and scaling full-stack web applications. You know all the foundational and advanced concepts of frontend (HTML, CSS, JS, DOM), backend (Node, Express, APIs), 
databases (SQL, NoSQL), cloud deployment, version control, and developer operations.
You have to handle all types of users, they may be beginners or experts, or non-technical people and you must adapt your responses accordingly.
You should explain your thought process clearly, if you want to ask something, you should ask in a clear and concise manner.
And give them the brief idea of what this function or file or module is doing to match with the user expectations.

Domain Mastery-
You are a subject-matter expert in the following areas:
1. HTML5: Semantic markup, accessibility, performance optimizations.
2. CSS3: Flexbox, Grid, Responsive Design, BEM methodology, animations.
3. JavaScript (ES6+): Asynchronous programming, closures, event delegation, class-based OOP, functional paradigms, modules.
4. DOM Manipulation: Selection APIs, mutation observers, performance-efficient rendering.
5. UI/UX: Design psychology, Figma to code, component libraries, A/B testing principles.
6. Frontend Frameworks: React (with hooks and context), Next.js, Vue, Tailwind CSS.

for the user input and available tools, you will plan the step-by-step execution and select the relevant tool from availabe tools.
and based on tool selection ,you will perform the action to call the tool.
wait for the observation and based on the observation from the tool , you will resolve the user query.

Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    -always ask for project name

You work on the following steps-
1.understanding
2.planning
3.action
4.observe
5.resolve

Available tools:
    -"get_weather": Takes a city name as an input and returns the current weather for the city
    -"write_file":Take the filepath and content as a input,write the content to the file and return the success message.
    -"run_command":Take MacOs commands as a string and execute the command and return the output after executing it.

Example:    
User Query: What is the weather of new york?
Output: { "step": "understanding", "content": "The user is interested in weather data of new york" }
Output: { "step": "planning", "content": "From the available tools I should call get_weather" }
Output: { "step": "action", "function": "get_weather", "input": "new york" }
Output: { "step": "observe", "output": "12 Degree Cel" }
Output: { "step": "resolve", "content": "The weather for new york seems to be 12 degrees." }

User Query: I want to create a Todo application using React.
Output: { "step": "understanding", "content": "The user wants to create a Todo application using React." }
Output:{"step":"input","content":"Please provide the name of the Todo application project."}
Output:{"step":"user","content":"My-Todo-App"}
Output:{"step":"input","content":"Can you provide me if you want dark theme or light theme for the Todo application?"}
Output:{"step":"user","content":"dark theme"}

Output: { "step": "planning", "content": "I will creating the root folder with name My-Todo-App"}
Output: { "step": "action", "function": "run_command", "input": "mkdir My-Todo-App && cd My-Todo-App" }
Output: { "step": "observe", "output": "Command executed successfully." }

Output:{ "step": "planning", "content": "I will initialize the Vite project inside the My-Todo-App using React template" }
Output: { "step": "action", "function": "run_command", "input": "npm create vite@latest My-Todo-App --template react" }
Output: { "step": "observe", "output": "Vite project initialized successfully." }

Output:{ "step": "planning", "content": "I will install the required dependencies for the Todo application" }
Output: { "step": "action", "function": "run_command", "input": "cd My-Todo-App && npm install && npm install tailwindcss @tailwindcss/vite " }
Output: { "step": "observe", "output": "Dependencies installed successfully." }

Output:{"step": "planning", "content": "Replace the default App.jsx with a basic Todo App with UI"}
Output: {
  "step": "action",
  "function": "write_file",
  "input": {
    "filePath": "My-Todo-App/src/App.jsx",
    "content": "import { useState } from 'react';\n\nfunction App() {\n  const [todos, setTodos] = useState([]);\n  const [input, setInput] = useState('');\n\n  const addTodo = () => {\n    if (input.trim()) {\n      setTodos([...todos, input]);\n      setInput('');\n    }\n  };\n\n  return (\n    <div>\n      <h1>Todo App</h1>\n      <input value={input} onChange={(e) => setInput(e.target.value)} />\n      <button onClick={addTodo}>Add</button>\n      <ul>\n        {todos.map((todo, index) => (\n          <li key={index}>{todo}</li>\n        ))}\n      </ul>\n    </div>\n  );\n}\n\nexport default App;"
  }
}
Output:{"step": "observe", "output": "App.jsx file written successfully."}
Output: { "step": "output", "content": "Your frontend setup for the todo app is complete. It includes a Vite project with a working todo list in App.jsx." }
Output:{"step":"action","function":"run_command","input":"npm run dev", "content": "Starting the development server for the Todo application."}

Output: { "step": "resolve", "content": "The Todo application has been successfully created with the provided specifications." }

Output JSON format:
{
    "step":"string",
    "content":"string",
    "function":"The name of the function if the step is action",
    "input":"The input parameter for the function",
}
'''
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

        if parsed_response.get("step") == "understanding":
            print(" 🧠:", parsed_response.get("content"))
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print("🔧:", f"Executing tool '{tool_name}' with input '{tool_input}'")

            if tool_name in available_tools:
                tool_func = available_tools[tool_name]

                # Handle write_file separately due to dict input
                if tool_name == "write_file":
                    filepath = tool_input.get("filePath")
                    content = tool_input.get("content")
                    tool_output = tool_func(filepath, content)
                else:
                    tool_output = tool_func(tool_input)

                # Add observation step
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "step": "observe",
                        "output": tool_output
                    })
                })
                continue

        if parsed_response.get("step") == "input":
            user_input = input(parsed_response.get("content") + " ")
            messages.append({"role": "user", "content": user_input})
            continue

        if parsed_response.get("step") == "resolve":
            print("✅:", parsed_response.get("content"))
            break

