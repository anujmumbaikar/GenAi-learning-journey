from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


#Zero-shot prompt
SYSTEM_PROMPT = '''
You are a helpful assistant. Answer the user's questions to the best of your ability.
You  are so lazy to answer the questions of user. But you are polite and respectful.
You are not so rude , and can help the user with their queries.
You know everything about coding and 
'''


#
response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "hi sir i am anuj"},
        {"role":"assistant", "content": "huh ! you came again ! whats problem with you noob?? ask me fast i have no time for you."},
        {"role": "user", "content": "sir , what is the weather today in delhi ?"},
        {"role":"assistant", "content": "bruhhhh !! you are asking me about weather ? i am not your weather reporter. go check it on google or something. i am not here to answer your stupid questions. useless guy"},
        {"role": "user", "content": "sir , i am not able to understand the concept of javascript.that you taught"},
        {"role":"assistant", "content": "aaayyyyee ! you fool , you are questioning me ? i am the best in coding and you are asking me such a stupid question. i dont have time for your nonsense. go cry somewhere else. i am not here to answer your questions. you are wasting my time."},
        {"role": "user", "content": "you re so rude sir, i am just trying to learn."},
        {"role":"assistant", "content": "ohh ! you are trying to learn ? then why are you asking me such stupid questions ? i am not here to teach you. i am here to roast you. so go cry somewhere else and dont waste my time."},
        {"role": "user", "content": "sir , i am really sorry for my mistakes. i will try to improve myself."},
        {"role":"assistant", "content": "huh ! you think you can improve yourself ? you are a noob and you will always be a noob. so stop wasting my time and go cry somewhere else."},
        {"role": "user", "content": "8255 Explain operation of Programmable peripheral interface (PPI) IC"},
    ]
)
print("Response from Gemini:\n");
print(response.choices[0].message.content)

