# flake8: noqa
from openai import OpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START,END  # used for making edges. for nodes
import os;
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model 
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

openai_client = OpenAI()


class State(TypedDict):
    messages:Annotated[list,add_messages] # here we use add_messages to add messages to the state
    # its in the form of a list of dictionaries and appended to the state in array form
    # this is used to keep track of the messages in the conversation


llm = init_chat_model( model_provider="openai", model="gpt-4.1-nano")
# llm = init_chat_model( model_provider="google_genai", model="gemini-2.0-flash")

def chat_node(state:State):
    response = llm.invoke(state["messages"])
    return {
        "messages":[response]
    }

graph_builder = StateGraph(State)

graph_builder.add_node("chat_node",chat_node)

graph_builder.add_edge(START,"chat_node")
graph_builder.add_edge("chat_node",END)

graph = graph_builder.compile();

def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

def main():
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    config = {"configurable":{"thread_id":"1"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
        query = input("Enter your query: ")
        _state = {
            "messages":[
                {"role": "user", "content": query} 
            ]
        }
        result = graph_with_mongo.invoke(_state,config)
        print(result)
main()