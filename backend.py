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
    
    database_url = database_url.rstrip("/")
    if "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    
    return database_url

# url = get_database_url()
# print(url)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("groq api key is missing")

# LLM 
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY
)


# State

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# flight agent
def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight result fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# hotel agent
def Hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    Hotel_results = tavily_search(query)

    return {
        "hotel_results": Hotel_results,
        "messages": [
            AIMessage(content="Hotel informations fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# itinerary agent 

def itinerary_agent(state: TravelState):
    prompt = f"""
        create a complete travel itinerary.

        User Query:
            {state['user_query']}
        flight Query :
            {state['flight_results']}
        Hotel Result:
            {state['hotel_results']}
        Make the itinery practical , buget-aware, and easy to follow
        """
    res = llm.invoke([
        SystemMessage(content="You are an expert traveller Planner"),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": res.content,
        "messages": [res],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# final agent

def final_agent(state: TravelState):
    final_prompt = f"""
    Generate the final travel response for the user.
        User Request:
            {state['user_query']}
        flights :
            {state['flight_results']}
        Hotel Result:
            {state['hotel_results']}
        Itinerary:
            {state['itinerary']}
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

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", Hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

# database checkpoint
Database_url = get_database_url()

con_db = psycopg.connect(
    Database_url,
    autocommit=True,
    row_factory=dict_row
)

checkpointer = PostgresSaver(con_db)
checkpointer.setup()

travel_graph = graph.compile(checkpointer=checkpointer)


def run_travel_agent(user_input: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = travel_graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }
