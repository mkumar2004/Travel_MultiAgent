import re
from typing import Any, Dict, List, Optional


def parse_flights_to_array(text: str) -> List[Dict[str, Any]]:
    """Parse raw flight results string into an array of flight objects."""
    if not text or "No flights found" in text or "Flight Api error" in text:
        return []

    flights: List[Dict[str, Any]] = []
    blocks = [b.strip() for b in re.split(r"\n\s*\.\.\.\s*\n", text) if "Airline:" in b]

    for b in blocks:
        airline_m = re.search(r"Airline:\s*(.+)", b)
        flight_no_m = re.search(r"Flight:\s*(.+)", b)
        status_m = re.search(r"Status:\s*(.+)", b)

        dep_airport_m = re.search(r"Departure:.*?-\s*Airport:\s*(.+)", b, re.DOTALL)
        dep_iata_m = re.search(r"Departure:.*?-\s*IATA:\s*(.+)", b, re.DOTALL)
        dep_terminal_m = re.search(r"Departure:.*?-\s*Terminal:\s*(.+)", b, re.DOTALL)
        dep_gate_m = re.search(r"Departure:.*?-\s*Gate:\s*(.+)", b, re.DOTALL)
        dep_scheduled_m = re.search(r"Departure:.*?-\s*Scheduled:\s*(.+)", b, re.DOTALL)
        dep_delay_m = re.search(r"Departure:.*?-\s*Delay:\s*(.+)", b, re.DOTALL)

        arr_airport_m = re.search(r"Arrival:.*?-\s*Airport:\s*(.+)", b, re.DOTALL)
        arr_iata_m = re.search(r"Arrival:.*?-\s*IATA:\s*(.+)", b, re.DOTALL)
        arr_terminal_m = re.search(r"Arrival:.*?-\s*Terminal:\s*(.+)", b, re.DOTALL)
        arr_gate_m = re.search(r"Arrival:.*?-\s*Gate:\s*(.+)", b, re.DOTALL)
        arr_scheduled_m = re.search(r"Arrival:.*?-\s*Scheduled:\s*(.+)", b, re.DOTALL)
        arr_delay_m = re.search(r"Arrival:.*?-\s*Delay:\s*(.+)", b, re.DOTALL)

        def _first_line(m):
            return m.group(1).split("\n")[0].strip() if m else None

        flights.append({
            "airline": airline_m.group(1).strip() if airline_m else None,
            "flight_number": flight_no_m.group(1).strip() if flight_no_m else None,
            "status": status_m.group(1).strip() if status_m else None,
            "departure": {
                "airport": _first_line(dep_airport_m),
                "iata": _first_line(dep_iata_m),
                "terminal": _first_line(dep_terminal_m),
                "gate": _first_line(dep_gate_m),
                "scheduled": _first_line(dep_scheduled_m),
                "delay": _first_line(dep_delay_m),
            },
            "arrival": {
                "airport": _first_line(arr_airport_m),
                "iata": _first_line(arr_iata_m),
                "terminal": _first_line(arr_terminal_m),
                "gate": _first_line(arr_gate_m),
                "scheduled": _first_line(arr_scheduled_m),
                "delay": _first_line(arr_delay_m),
            }
        })

    return flights


def parse_hotels_to_array(text: str) -> List[Dict[str, Any]]:
    """Parse raw hotel search text into an array of hotel/search result objects."""
    if not text:
        return []

    hotels: List[Dict[str, Any]] = []
    pattern = re.compile(
        r"^\d+\.\s+\*\*(.+?)\*\*\s*\n\s*(https?://[^\s]+)\s*\n([\s\S]*?)(?=(?:^\d+\.\s+\*\*)|\Z)",
        re.MULTILINE
    )

    for match in pattern.finditer(text):
        title = match.group(1).strip()
        url = match.group(2).strip()
        snippet = match.group(3).strip()

        nested_items = re.findall(r"###\s*\d*\.?\s*([^\n]+)", snippet)
        cleaned_places = [re.sub(r"^[0-9\.\s]+", "", p).strip() for p in nested_items if p.strip()]

        hotels.append({
            "title": title,
            "url": url,
            "snippet": snippet,
            "recommended_places": cleaned_places
        })

    return hotels


def parse_markdown_table_to_array(text: str) -> List[Dict[str, str]]:
    """Convert any markdown table (| col1 | col2 |) into a list of row dictionaries."""
    lines = [
        line.strip()
        for line in text.strip().split("\n")
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if len(lines) < 3:
        return []

    # Clean headers (remove bold, asterisks, extra spaces)
    raw_headers = [h.strip() for h in lines[0].strip("|").split("|")]
    headers = [re.sub(r"[*_`]", "", h).strip() for h in raw_headers]

    rows: List[Dict[str, str]] = []
    for line in lines[2:]:
        # Ignore divider rows (|---|---|)
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue

        raw_cols = [c.strip() for c in line.strip("|").split("|")]
        if len(raw_cols) == len(headers):
            clean_row = {}
            for h, v in zip(headers, raw_cols):
                cleaned_val = re.sub(r"<br\s*/?>", " ", v)
                cleaned_val = re.sub(r"[*_`]", "", cleaned_val).strip()
                clean_row[h] = cleaned_val
            rows.append(clean_row)

    return rows


def parse_itinerary_days_to_array(text: str) -> List[Dict[str, Any]]:
    """
    Extracts day-by-day plan from either markdown tables or day headers:
    e.g. '### **Day 0 – Travel to Goa**'
    """
    if not text:
        return []

    # First attempt: table parsing
    table_items = parse_markdown_table_to_array(text)
    if table_items:
        return table_items

    # Second attempt: parse day headers like '### **Day 0 – ...**'
    days: List[Dict[str, Any]] = []
    day_pattern = re.compile(
        r"###\s+\*\*Day\s*(\d+[^\*]*)\*\*\s*\n([\s\S]*?)(?=(?:###\s+\*\*Day)|\Z)",
        re.MULTILINE
    )
    for day_label, body in day_pattern.findall(text):
        cleaned_day = f"Day {day_label.strip()}"
        cleaned_body = body.strip().rstrip("-").strip()

        # Parse bullet points inside each day
        bullets = [
            re.sub(r"^[-*•]\s*", "", line).strip()
            for line in cleaned_body.split("\n")
            if line.strip().startswith(("-", "*", "•"))
        ]

        days.append({
            "day": cleaned_day,
            "description": cleaned_body,
            "activities": bullets if bullets else [cleaned_body]
        })

    return days


def parse_markdown_sections(text: str) -> Dict[str, Any]:
    """
    Parse markdown headers (## Section) into a structured dictionary with
    both raw text and auto-parsed items/table arrays.
    """
    if not text:
        return {}

    sections: Dict[str, Any] = {}
    pattern = re.compile(r"^##\s+([^\n]+)\s*\n([\s\S]*?)(?=(?:^##\s+)|\Z)", re.MULTILINE)

    for title, content in pattern.findall(text):
        clean_title = re.sub(r"^[0-9️⃣\uFE0F\.\s\-\:]+", "", title).strip()
        clean_content = content.strip().rstrip("-").strip()

        # Check for tables first
        table_array = parse_markdown_table_to_array(clean_content)

        # If no table, but it's an itinerary section, check for day headers
        if not table_array and ("itinerary" in clean_title.lower() or "day" in clean_title.lower()):
            table_array = parse_itinerary_days_to_array(clean_content)

        sections[clean_title] = {
            "content": clean_content,
            "items": table_array if table_array else []
        }

    return sections
