# flake8:noqa
from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small",
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4.1-mini"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "vector_db",
            "port": 6333
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://neo4j:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    },
}

client = OpenAI()
mem_client = Memory.from_config(config)

def chat():
    while True:
        query = input(">>> ")
        relevant_memories = mem_client.search(
            query=query,
            user_id="Anuj",
        )
        memories = {
            f"ID:{mem.get('id')}, memory:{mem.get('memory')}"
            for mem in relevant_memories.get("results", [])
        }

        SYSTEM_PROMPT = f"""
            You are a memory-aware assistant that responds to user queries based on the user's memories.
            You are given past memories and facts about the user.
            If you don't know the answer, say "I don't know" or "I am not sure."

            User memory:
            {json.dumps(list(memories), indent=2)}
        """
        result = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]
        )

        response = result.choices[0].message.content
        print(response)
        # Store in memory
        # this should be done in queue , cuz it takes time , to do it asynchronusly
        mem_client.add([
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ], user_id="Anuj")

chat()
