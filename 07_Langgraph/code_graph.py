# flake8: noqa
from openai import OpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START,END  # used for making edges. for nodes
import os;
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
gemini_client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
openai_client = OpenAI()


class ClassifyMessageResponse(BaseModel):  # pydantic model to validate the response.
    is_coding_question: bool
    
class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str

class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage:str| None
    is_coding_question:bool| None

def classify_message(state:State):
    print("🧠Classifying message...")
    query = state["user_query"];
    SYSTEM_PROMPT = """
    You are an Ai Assistant . your job is to detect if the user's query is related
    to coding question or not.
    Return the response in specified JSON boolean only.
    """
    
    # structred output/responses means we can get response according to our needs.
    # here we want to get a boolean response. to check if the query is related to coding or not.
    # validation library - pydantic is used to validate the response.
    
    
    #and since we want structured output, we have to use beta and parse the response.
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ],
    )
    # earlier we have seen that, while building , we used to give JSON response. which has not garunteed that the response will be in JSON format.
    # in cursor.py we used to give rules in SYSTEM_PROMPT to get the response in JSON format.
    # but that has no garunteed that the response will be in JSON format. always. 
    # but here we are using structured output, which will garuntee that the response will be in JSON format.  
    is_coding_question = response.choices[0].message.parsed.is_coding_question;
    state["is_coding_question"] = is_coding_question
    return state
    
    
# whenever we do routing, we have to use Literal , which
# means , it tells where it can go next.
# here we have two options, either it can go to general_query or coding_query.
def route_query(state:State) ->Literal["general_query", "coding_query"]:
    print("🧭Routing query...")
    is_coding = state["is_coding_question"]
    
    if is_coding:
        return "coding_query"
    
    return "general_query"

def general_query(state:State):
    print("💬Handling general query...")
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are an AI Assistant. Your job is to answer the user's query.
    You should provide a detailed and accurate response based on the user's input.
    If you don't know the answer, you should say "I don't know".
    """
    response = gemini_client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content":SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )
    state["llm_result"] = response.choices[0].message.content
    return state

def coding_query(state:State):
    print("💻Handling coding query...")
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are an AI Coding Expert. Your job is to answer the user's coding-related query.
    You should provide a detailed and accurate response based on the user's input.
    You know everything about coding and programming languages.
    You hv done P.hd in Computer Science.
    dont answer any question which is not related to coding.
    If you don't know the answer, you should say "I don't know".
    You should also provide the code in the response if applicable.
    Always give examples of code snippets in your response.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content":SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )
    state["llm_result"] = response.choices[0].message.content
    return state

def coding_validate(state:State):
    print("🔍Validating coding query...")
    query = state["user_query"]
    llm_result = state["llm_result"]
    SYSTEM_PROMPT = f"""
    You are an Expert in calculating the accuracy of the code.
    And how much optimal the code is. which means how much efficient the code is.
    Your job is to validate the code provided by the user.
    Return the percentage of accuracy of the code.
    User Query:{query}
    Code:{llm_result}
    """
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ],
    )
    state["accuracy_percentage"]=response.choices[0].message.parsed.accuracy_percentage
    return state


graph_builder = StateGraph(State)
#Define the nodes
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate", coding_validate)

#Define the edges
graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "coding_validate")
graph_builder.add_edge("coding_validate", END)

graph = graph_builder.compile()
def main():
    user_query = input("Enter your query: ")
    _state = State(
        user_query=user_query, 
        llm_result=None, 
        accuracy_percentage=None, 
        is_coding_question=None
    )
    # result = graph.invoke(_state)
    # print("Result:", result)
    
    #streaming the events (streaming the graph)
    for event in graph.stream(_state):
        print("Event", event)
    
main()
