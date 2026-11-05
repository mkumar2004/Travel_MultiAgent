from pathlib import Path
import json
import traceback
import uvicorn

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend import run_travel_agent
from tools.parser import (
    parse_flights_to_array,
    parse_hotels_to_array,
    parse_markdown_sections,
    parse_markdown_table_to_array
)


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            separators=(", ", ": ")
        ).encode("utf-8")

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="TripMate AI",
    description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
    version="1.0.0",
    default_response_class=PrettyJSONResponse
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")






class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return PrettyJSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        result = run_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        flights_array = parse_flights_to_array(result.get("flight_results", ""))
        hotels_array = parse_hotels_to_array(result.get("hotel_results", ""))
        sections = parse_markdown_sections(result.get("answer", ""))

        # If live flight API had no results, extract flights from the final LLM answer table
        if not flights_array and "Flight Information" in sections:
            flight_items = sections["Flight Information"].get("items", [])
            if flight_items:
                flights_array = flight_items

        # Extract structured day-by-day itinerary table or day list if available
        itinerary_array = []
        for sec_name, sec_val in sections.items():
            if "itinerary" in sec_name.lower() and sec_val.get("items"):
                itinerary_array = sec_val["items"]
                break

        return PrettyJSONResponse(
            content={
                "success": True,
                "thread_id": result["thread_id"],
                "answer": result["answer"],
                "sections": sections,
                "flights": flights_array,
                "hotels": hotels_array,
                "itinerary_schedule": itinerary_array,
                "flight_results": result["flight_results"],
                "hotel_results": result["hotel_results"],
                "itinerary": result["itinerary"],
                "llm_calls": result["llm_calls"],
            }
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

        return PrettyJSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )



@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})



if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )