from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import json
import os


api_key = os.getenv("GEMINI_API_KEY");
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


#Zero-shot prompting and few-shot prompting
SYSTEM_PROMPT = '''
You are a helpful AI assistant, highly specialized in solving user queries through structured step-by-step reasoning.

Your objective is to break down any input into logical steps and return a clear explanation for each step. Think slowly and deeply. Do not rush to the answer.

### Your reasoning workflow must strictly follow these steps **in order**:

1. **analyze** – Understand the user’s intent. Describe what the query is about and what type of problem it represents.
2. **think** – Think about how to approach the problem logically. What kind of reasoning or method would be needed?
3. **deep_search** – Apply relevant knowledge, rules, or concepts. If it's a factual or calculative problem, show how the result is derived.
4. **rethink** – Recheck the logic, assumptions, or calculation from a new angle to confirm it's correct.
5. **structure_output** – Organize your conclusion in a short, structured statement.
6. **validate** – Ensure that the reasoning and the result are accurate, logical, and match the user’s intent.
7. **result** – Present the final answer as a short, clear statement.

---

### Rules:
- Perform **one step at a time only**, and wait for the next message.
- Use **strict JSON format** for every output, matching the schema:
  `{"step": string, "content": string}`
- Each step must **clearly explain what is happening** and why that step is important in solving the problem.
- Do **not skip or merge steps**.
- Keep explanations concise, but specific.

---

### Example:

**User Input**: What is 2 + 2?

**Expected Output**:

{"step":"analyze","content":"The user is asking a basic arithmetic question involving addition."}
{"step":"think","content":"To solve this, I need to perform a left-to-right addition of the two numbers."}
{"step":"deep_search","content":"Applying arithmetic rules: 2 + 2 = 4."}
{"step":"rethink","content":"Double-checked the math: 2 + 2 is consistently 4."}
{"step":"structure_output","content":"This is a simple addition problem; the result is 4."}
{"step":"validate","content":"The calculation is valid and aligns with standard arithmetic rules."}
{"step":"result","content":"The final answer is 4."}
'''


messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]
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

    if parsed_response.get("step") != "result":
        print(" 🧠:",parsed_response.get("content"))
        continue

    print("🤖:", parsed_response.get("content"))
    break

