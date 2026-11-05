import os
import certifi
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict, Annotated
import operator
import uuid
import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage
)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

def get_database_url():
    database_url = os.getenv("DATA_BASE_URL")

    if not database_url:
        raise ValueError(
            "Database Url is Missing"
        )
    
    if "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    
    return database_url

# url = get_database_url()
# print(url)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError ( "groq api key is missing")

# LLM 
llm = ChatGroq(
     model="llama-3.3-70b-versatile",
     api_key=GROQ_API_KEY
)


#State

class TravelSate(TypedDict):
    messages : Annotated[list[AnyMessage],operator.add]
    user_query : str
    flight_results : str
    hotel_results : str
    itinerary : str
    llm_calls ; int


# flight agent
def flight_agent(state : TravelSate):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_result":flight_data,
        "message":[
            AIMessage(content="Flight result fetched")

        ],
        "llm_calls":State.get("llm_calls",0) + 1
    }
#hotel agent
def Hotel_agent(state:TravelSate):
    query = f"Best hotels for {state['user_query']}"
    Hotel_results = tavily_search(query)

    return {
        "hotel_results": Hotel_results,
        "message":[
            AIMessage(content="Hotel informations fetched")
        ],
        "llm_calls" : state.get("llm_calls",0)+1
    }

#itineray agent 

def itinerary_agent(state:TravelSate):
    promot = f"""
        create a complete travel itinerary.

        User Query:
            {state['user_query']}
        flight Query :
            {state['flights_results']}
        Hotel Result:
            {state['hotel_results']}
        Make the itinery practical , buget-aware, and easy to follow
        """
    res = llm.invoke([
        SystemMessage(content="You are an expert traveller Planner"),
        HumanMessage(content=promot)
    ])

    return {
        "itinerary" : res.content,
        "message" : [res],
        "llm_call" : state.get("llm_calls",0)+1
    }

# final agent

def final_agent(state: TravelSate):
    final_promot = f"""
    Generate the final travel response for the user.
        User Request:
            {state['user_query']}
        flights :
            {state['flights_results']}
        Hotel Result:
            {state['hotel_results']}
        Itinerary:
            { state['itinerary']}
    Format the final answer beautifully using these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight API may not provide ticket prices if pricing is unavailable.
- Keep the response useful for real travel planning.
"""

    response = llm.invoke([
        SystemMessage(content="You are a professional AI travel booking assistant."),
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
    

# Graph build

graph = StateGraph(TravelSate)

graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",Hotel_agent)
graph.add_node("itinerary_agent",itinerary_agent)
graph.add_node("final_agent",final_agent)

graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","itinerary_agent")
graph.add_edge("itinerary_agent","final_agent")
graph.add_edge("final_agent",END)

#database check point
Database_url = get_database_url()

con_db = psycopg.connect(
    Database_url,
    autocommit=True,
    row_factory=dict_row
)