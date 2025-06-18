# flake8:noqa
from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
config = {
    "version":"v1.1",
    "embedder":{
        "provider":"openai",
        "config":{
            "api_key":OPENAI_API_KEY,
            "model":"text-embedding-3-small",
        },
    },
    "llm":{"provider":"openai","config":{"api_key":OPENAI_API_KEY,"model":"gpt-4.1-mini"}},
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "host":"vector_db",
            "port":6333
        }
    }
}
client = OpenAI()
mem_client = Memory.from_config(config)
def chat():
    while True:
        query = input(">>>")
        result = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": query}
            ]
        )
        print(f"{result.choices[0].message.content}")
        
        #mem0 docs now we will add in mem0
        mem_client.add([
            {"role":"user","content":query},
            {"role":"assistant","content":result.choices[0].message.content}
        ],user_id="Anuj")

chat()