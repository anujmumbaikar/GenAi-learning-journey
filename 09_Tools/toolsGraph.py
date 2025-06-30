# flake8: noqa
from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START,END  # used for making edges. for nodes
from langchain.chat_models import init_chat_model 
from typing import Annotated
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition

load_dotenv()

#we have made a tool
# so in order to use this tool , we need decorator (from langchain_core.tools import tool)
# and description of the tool is given in the docstring of the function
@tool()
def add_two_numbers(a: int, b: int):
    """This tool adds two numbers"""
    return a + b

@tool()
def get_weather(city: str):
    """This tool returns the weather data about the given city"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error fetching weather data for {city}"
    return "The weather in " + city + " is " + response.text

tools=[get_weather,add_two_numbers]

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = init_chat_model( model_provider="openai", model="gpt-4.1-nano") #this llm doesnt know about the tool
llm_with_tools = llm.bind_tools(tools) # now this llm knows about the tool

tool_node = ToolNode(tools=tools)
def chat_node(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {
        "messages": [message]
    }
#     Tool Calls:
#     get_weather (call_xaN36uVbpj6Wh5h22lslNRwZ)
#     Call ID: call_xaN36uVbpj6Wh5h22lslNRwZ -> this call id is unique -> if i give panvel , mumabi,delhi, then it will get confuse . thats why we have unique call ids
#     Args:
#       city: Alibaug

graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("tools",tool_node)


graph_builder.add_edge(START, "chat_node")
graph_builder.add_conditional_edges("chat_node",tools_condition)
graph_builder.add_edge("tools", "chat_node")

graph = graph_builder.compile() 

def main():
    query = input("Enter your query: ")
    _state = {
        "messages": [
            {"role": "user", "content": query}
        ]
    }
    for event in graph.stream(_state):
        print("Event", event)
    
main()