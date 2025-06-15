# flake8: noqa
from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START,END
from langchain.chat_models import init_chat_model 
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command,interrupt
from dotenv import load_dotenv
import json
load_dotenv()

@tool()
def human_assistence(query:str)->str:
    """Request assistence from a human"""
    human_response = interrupt({"query":query})  # this saves the state to the db and kills the graph.
    
    return human_response


tools = [human_assistence]

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
llm = init_chat_model(model_provider="openai", model="gpt-4.1-mini")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state:State):
    message = llm_with_tools.invoke(state["messages"])
    return {
        "messages": [message]
    }
    
tool_node = ToolNode(tools=tools)
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("tools",tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot",tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)


def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

def user_chat():
    while True:
        DB_URI = "mongodb://admin:admin@mongodb:27017"
        config = {"configurable":{"thread_id":"22"}}
        with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
            graph_with_mongo = create_chat_graph(mongo_checkpointer)
            query = input("Enter your query: ")
            _state = {
                "messages":[
                    {"role": "user", "content": query} 
                ]
            }
            for event in graph_with_mongo.stream(_state,config,stream_mode='values'):
                if "messages" in event:
                    event["messages"][-1].pretty_print()


def admin_panel():
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    config = {"configurable":{"thread_id":"22"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = create_chat_graph(mongo_checkpointer)
        
        state = graph_with_mongo.get_state(config);
        last_message_of_that_state = state.values['messages'][-1];
        
        # if last message is tool_call then only we have to interrupt.
        # if last message is just hi,hello , then we dont hv to do anything.
        user_query = None
        tool_call = last_message_of_that_state.additional_kwargs.get("tool_calls", [])
        for call in tool_call:
            if call.get("function",{}).get('name') == "human_assistence":
                args = call["function"].get("arguments", "{}")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Error decoding JSON from tool call arguments.")
               
        print("User has a query",user_query)
        solution = input("Enter your solution: ")
        
        resume_graph = Command(resume={"data":solution})
        
        for event in graph_with_mongo.stream(resume_graph,config,stream_mode='values'):
            if "messages" in event:
                 event["messages"][-1].pretty_print()
admin_panel()