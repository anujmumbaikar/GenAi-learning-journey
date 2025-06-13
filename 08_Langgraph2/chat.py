# flake8: noqa
from openai import OpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START,END  # used for making edges. for nodes
import os;
from dotenv import load_dotenv
# langchain provides abstraction for most of the tasks
from langchain.chat_models import init_chat_model 
from typing import Annotated
from langgraph.graph.message import add_messages

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
# llm = init_chat_model( model_provider="google", model="gemini-2.0-flash")

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

def main():
    query = input("Enter your query: ")
    _state = {
         "messages":[
            {"role": "user", "content": query} 
         ]
    }
    result = graph.invoke(_state)
    print(result)
    
    
    # Little different output format, because we are using langchain's chat model. nothing different but just the output format.
    # {
    #      'messages': [
    #          HumanMessage(content='hello budd', additional_kwargs={}, response_metadata={}, id='d76eaf23-046d-4ea6-8c70-c2f3632ce30f'), 
    #          AIMessage(content='Hello! How can I assist you today?', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 9, 'prompt_tokens': 10, 'total_tokens': 19, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4.1-nano-2025-04-14', 'system_fingerprint': 'fp_38343a2f8f', 'id': 'chatcmpl-BhuVb86AMeGe0GCMJdHVX0oxM5pIW', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='run--8e487233-04df-4a5c-9af2-871678c95dbe-0', usage_metadata={'input_tokens': 10, 'output_tokens': 9, 'total_tokens': 19, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]
    # }
    
    
    # NOTE- one problem is there if a enter "hello , my name is anuj"
    # next time it will not remember the previous messages.. "I'm sorry, but I don't know your name. How can I assist you today?"
    # because our state is transient state(lasts for short time)which gets reset every time we invoke the graph.
    #once the invoke is done, the state is reset.
    # then whats the use of Annotation ?? 
    # -- if you have more nodes then , each node message will be appended the message in the state.
    # Thats where the concept checkpointing comes in.
main()