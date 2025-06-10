# flake8: noqa
from openai import OpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START,END  # used for making edges. for nodes
import os;
from dotenv import load_dotenv

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
    query:str
    llm_result:str | None
    
def chat_bot(state:State): #this is a node 1. 
    
    query = state['query']
    llm_response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "user", "content": query}
        ],
        max_tokens=100,
        temperature=0.7
    )
    result = llm_response.choices[0].message.content
    state['llm_result'] = result
    return state

graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot",chat_bot)
#Edges  
graph_builder.add_edge(START,"chat_bot")
graph_builder.add_edge("chat_bot",END)


# now compile the graphbuilder.
graph = graph_builder.compile()


def main():
    user = input(">>>")
    #Invoke the graph.
    _state = {
        "query":user,
        "llm_result":None
    }
    graph_result = graph.invoke(_state)
    print("graph_result",graph_result)
    
    
main()