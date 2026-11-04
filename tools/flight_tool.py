import os 
import certifi
import re
import airportsdata
import pycountry
import requests
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN", "DAC")
DEFAULT_ORIFIN_DATA = DEFAULT_ORIGIN_IATA

BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPOTTS = airportsdata.load("IATA")


COUNTRY_ALIASES = {
    # United States
    "usa": "US",
    "u.s.a.": "US",
    "u.s.": "US",
    "america": "US",
    "united states": "US",
    "united states of america": "US",

    # United Kingdom
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "great britain": "GB",
    "england": "GB",
    "united kingdom": "GB",

    # United Arab Emirates
    "uae": "AE",
    "u.a.e.": "AE",
    "emirates": "AE",
    "dubai": "AE",

    # India
    "india": "IN",
    "bharat": "IN",
    "hindustan": "IN",
    "republic of india": "IN",

    # Canada
    "canada": "CA",
    "can": "CA",

    # Australia
    "australia": "AU",
    "aus": "AU",

    # Germany
    "germany": "DE",
    "deutschland": "DE",

    # France
    "france": "FR",

    # Japan
    "japan": "JP",
    "nippon": "JP",
    "nihon": "JP",

    # China
    "china": "CN",
    "prc": "CN",
    "people's republic of china": "CN",

    # South Korea
    "south korea": "KR",
    "republic of korea": "KR",
    "korea, republic of": "KR",

    # North Korea
    "north korea": "KP",
    "dprk": "KP",

    # Singapore
    "singapore": "SG",

    # Malaysia
    "malaysia": "MY",

    # Indonesia
    "indonesia": "ID",

    # Pakistan
    "pakistan": "PK",

    # Bangladesh
    "bangladesh": "BD",

    # Sri Lanka
    "sri lanka": "LK",
    "ceylon": "LK",

    # Nepal
    "nepal": "NP",

    # New Zealand
    "new zealand": "NZ",
    "aotearoa": "NZ",

    # South Africa
    "south africa": "ZA",
    "rsa": "ZA",

    # Saudi Arabia
    "saudi arabia": "SA",
    "ksa": "SA",

    # Turkey
    "turkey": "TR",
    "türkiye": "TR",
    "turkiye": "TR",

    # Netherlands
    "netherlands": "NL",
    "holland": "NL",

    # Switzerland
    "switzerland": "CH",

    # Ireland
    "ireland": "IE",
    "republic of ireland": "IE",

    # Italy
    "italy": "IT",
    "italia": "IT",

    # Spain
    "spain": "ES",
    "españa": "ES",
    "espana": "ES",

    # Brazil
    "brazil": "BR",
    "brasil": "BR",

    # Russia
    "russia": "RU",
    "russian federation": "RU",

    # Mexico
    "mexico": "MX",
    "méxico": "MX",

    # Egypt
    "egypt": "EG",

    # Nigeria
    "nigeria": "NG",

    # Kenya
    "kenya": "KE",

    # Argentina
    "argentina": "AR",

    # Portugal
    "portugal": "PT",

    # Ukraine
    "ukraine": "UA",

    # Vietnam
    "vietnam": "VN",
    "viet nam": "VN",

    # Thailand
    "thailand": "TH",
    "siam": "TH",
}

COUNTRY_MAIN_AIRPORT = {
    "BD": "DAC",  # Bangladesh
    "IN": "DEL",  # India
    "JP": "NRT",  # Japan
    "US": "JFK",  # United States
    "GB": "LHR",  # United Kingdom
    "AE": "DXB",  # United Arab Emirates
    "SG": "SIN",  # Singapore
    "MY": "KUL",  # Malaysia
    "TH": "BKK",  # Thailand
    "ID": "CGK",  # Indonesia
    "CN": "PEK",  # China
    "KR": "ICN",  # South Korea
    "NP": "KTM",  # Nepal
    "QA": "DOH",  # Qatar
    "SA": "JED",  # Saudi Arabia
    "TR": "IST",  # Turkey
    "CA": "YYZ",  # Canada
    "AU": "SYD",  # Australia
    "DE": "FRA",  # Germany
    "FR": "CDG",  # France
    "IT": "FCO",  # Italy
    "ES": "MAD",  # Spain
    "BR": "GRU",  # Brazil
    "RU": "SVO",  # Russia
    "NZ": "AKL",  # New Zealand
    "ZA": "JNB",  # South Africa
    "PK": "KHI",  # Pakistan
    "LK": "CMB",  # Sri Lanka
    "MV": "MLE",  # Maldives
    "VN": "SGN",  # Vietnam
    "PH": "MNL",  # Philippines
    "EG": "CAI",  # Egypt
    "NG": "LOS",  # Nigeria
    "KE": "NBO",  # Kenya
    "MX": "MEX",  # Mexico
    "AR": "EZE",  # Argentina
    "CH": "ZRH",  # Switzerland
    "NL": "AMS",  # Netherlands
    "IE": "DUB",  # Ireland
    "PT": "LIS",  # Portugal
    "GR": "ATH",  # Greece
    "SE": "ARN",  # Sweden
    "NO": "OSL",  # Norway
    "DK": "CPH",  # Denmark
    "FI": "HEL",  # Finland
    "PL": "WAW",  # Poland
    "AT": "VIE",  # Austria
    "BE": "BRU",  # Belgium
    "CZ": "PRG",  # Czechia
    "IL": "TLV",  # Israel
    "OM": "MCT",  # Oman
    "KW": "KWI",  # Kuwait
    "BH": "BAH",  # Bahrain
    "JO": "AMM",  # Jordan
    "ET": "ADD",  # Ethiopia
    "MA": "CMN",  # Morocco
    "CL": "SCL",  # Chile
    "CO": "BOG",  # Colombia
    "PE": "LIM",  # Peru
}

CITY_MAIN_AIRPORT = {
    # Bangladesh
    "dhaka": "DAC",

    # India
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "kolkata": "CCU",
    "chennai": "MAA",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "kochi": "COK",
    "cochin": "COK",
    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",
    "coimbatore": "CJB",
    "madurai": "IXM",
    "tiruchirappalli": "TRZ",
    "trichy": "TRZ",
    "goa": "GOI",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "visakhapatnam": "VTZ",
    "vizag": "VTZ",
    "mangalore": "IXE",
    "mangaluru": "IXE",
    "tirupati": "TIR",
    "bhubaneswar": "BBI",
    "varanasi": "VNS",
    "amritsar": "ATQ",
    "srinagar": "SXR",
    "port blair": "IXZ",

    # Japan
    "tokyo": "NRT",
    "osaka": "KIX",
    "kyoto": "KIX",
    "nagoya": "NGO",
    "sapporo": "CTS",
    "fukuoka": "FUK",

    # United States
    "new york": "JFK",
    "los angeles": "LAX",
    "san francisco": "SFO",
    "chicago": "ORD",
    "washington": "IAD",
    "miami": "MIA",
    "boston": "BOS",
    "seattle": "SEA",
    "las vegas": "LAS",
    "dallas": "DFW",
    "houston": "IAH",
    "atlanta": "ATL",
    "orlando": "MCO",
    "san diego": "SAN",

    # United Kingdom
    "london": "LHR",
    "manchester": "MAN",
    "birmingham": "BHX",
    "edinburgh": "EDI",
    "glasgow": "GLA",

    # United Arab Emirates
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",

    # Singapore
    "singapore": "SIN",

    # Malaysia
    "kuala lumpur": "KUL",
    "penang": "PEN",
    "langkawi": "LGK",

    # Thailand
    "bangkok": "BKK",
    "phuket": "HKT",
    "chiang mai": "CNX",

    # Indonesia
    "jakarta": "CGK",
    "bali": "DPS",
    "denpasar": "DPS",

    # China
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "hong kong": "HKG",

    # South Korea
    "seoul": "ICN",
    "busan": "PUS",

    # Nepal
    "kathmandu": "KTM",

    # Qatar
    "doha": "DOH",

    # Saudi Arabia
    "jeddah": "JED",
    "riyadh": "RUH",
    "medina": "MED",

    # Canada
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",

    # Australia
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "adelaide": "ADL",

    # Germany
    "frankfurt": "FRA",
    "munich": "MUC",
    "berlin": "BER",

    # France
    "paris": "CDG",
    "nice": "NCE",
    "lyon": "LYS",

    # Italy
    "rome": "FCO",
    "milan": "MXP",
    "venice": "VCE",

    # Spain
    "madrid": "MAD",
    "barcelona": "BCN",

    # Netherlands
    "amsterdam": "AMS",

    # Switzerland
    "zurich": "ZRH",
    "geneva": "GVA",

    # Turkey
    "istanbul": "IST",
    "ankara": "ESB",

    # Sri Lanka
    "colombo": "CMB",

    # Pakistan
    "karachi": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",

    # New Zealand
    "auckland": "AKL",
    "wellington": "WLG",
    "christchurch": "CHC",

    # South Africa
    "johannesburg": "JNB",
    "cape town": "CPT",

    # Egypt
    "cairo": "CAI",

    # Brazil
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",

    # Mexico
    "mexico city": "MEX",

    # Ireland
    "dublin": "DUB",

    # Portugal
    "lisbon": "LIS",

    # Russia
    "moscow": "SVO",

    # Vietnam
    "ho chi minh city": "SGN",
    "hanoi": "HAN",

    # Philippines
    "manila": "MNL",

    # Maldives
    "male": "MLE",
}

# cleaning data

def Clean_text(text:str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ",text)
    text = re.sub(r"\s+", " ",text)
    stop_words = [
        "fight", "fights" , "tickets" , "trip" , "travel",
        "plan" , "complete" , "days" , "day" , "including" , "hotels",
        "hotels", "sightseeing" , "under" , "budget" , "info" , "information"
    ]
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()

# country name => code 
def country_name_to_code(text: str):
    text = Clean_text(text)

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]
    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass
    # Detected country name inside longer text
    for country in pycountry.countries:
        country_name = country.name.lower()
        if country_name in text:
            return country.alpha_2
    
    for alias, code in COUNTRY_ALIASES.items():
        if alias in text:
            return code 
    return None 

# airport matches for country
def airports_country_matches(airport: dict, country_code: str) -> bool:
    airport_country = str(airport.get("country", " ")).upper().strip()
    if airport_country == country_code:
        return True
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except Exception:
        pass
    return False

airports_country_matcges = airports_country_matches

# best airports
def get_best_airports(country_code: str):
    perferred = COUNTRY_MAIN_AIRPORT.get(country_code)

    if perferred and perferred in AIRPOTTS:
        return perferred
    candidates = []

    for data, airports in AIRPOTTS.items():
        if not data:
            continue
        if airports_country_matches(airports, country_code):
            name = str(airports.get("name", " ")).lower()
            city = str(airports.get("city", " ")).lower()

            score = 0
            if "international" in name:
                score += 50
            if "intl" in name or "int1" in name:
                score += 40
            if "capital" in name or "captial" in name:
                score += 20
            if city:
                score += 5
            candidates.append((score, data))
    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]
 
# mention location
def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions

# location for data

def resolve_location_to_iata(location: str):
    if not location:
        return None
    raw_loc = location.strip()

    # 1. Exact uppercase 3-letter IATA code (e.g. "DEL", "BOM", "DAC")
    if raw_loc.isupper() and len(raw_loc) == 3 and raw_loc in AIRPOTTS:
        return raw_loc
        
    loc_clean = Clean_text(raw_loc)
    
    if not loc_clean:
        return None
    
    # 2. Known city mapping (e.g. "goa" -> "GOI", "chennai" -> "MAA", "mumbai" -> "BOM")
    if loc_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[loc_clean]
    
    # 3. Country mapping (e.g. "india" -> "IN" -> "DEL")
    country_code = country_name_to_code(raw_loc) or country_name_to_code(loc_clean)
    if country_code:
        best_airport = get_best_airports(country_code)
        if best_airport:
            return best_airport

    # 4. Any 3-letter code match in airport database
    if len(raw_loc) == 3 and raw_loc.upper() in AIRPOTTS:
        return raw_loc.upper()

    city_matches = []

    for data, airport in AIRPOTTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == loc_clean:
            score += 100 
        elif loc_clean in name:
            score += 70
        if "international" in name:
            score += 10
        
        if score > 0:
            city_matches.append((score, data))
    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]
    return None

resolve_location_data = resolve_location_to_iata

def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()

#routes for give data
def parse_route(query: str):
    """
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        dest_mentions = find_location_mentions(q[:match.start()])
        if dest_mentions:
            arr_iata = resolve_location_to_iata(dest_mentions[0])
            return dep_iata, arr_iata
        return dep_iata, None

    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        origin_mentions = find_location_mentions(q[:match.start()])
        if origin_mentions:
            dep_iata = resolve_location_to_iata(origin_mentions[0])
            return dep_iata, arr_iata
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None



#searchflight data
def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return "Missing Api Keys"
    
    dep_data, arr_data = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100)
    }
    if dep_data:
        params["dep_iata"] = dep_data
    if arr_data:
        params["arr_iata"] = arr_data
    try:
        res = requests.get(BASE_URL, params=params, timeout=30)
        data = res.json()
    except requests.exceptions.RequestException as e:
        return f"Flight Api failed: {e}"
    except ValueError:
        return "Flight Api Falied with Invlalid json"
    
    if "error" in data:
        error = data["error"]
        return (
            "Flight Api error:\n"
            f"code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    route_info = "Global Live Flights"

    if dep_data and arr_data:
        route_info = f"Live flights from {dep_data} to {arr_data}"
    elif dep_data:
        route_info = f"Live flights from {dep_data}"
    elif arr_data:
        route_info = f"live flights to {arr_data}"
    
    flight_data = data.get("data", [])
    if not flight_data:
        return f"{route_info}\n\nNo flights found."

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]
    
    return f"{route_info}\n\n" + "\n\n...\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 dats Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info ")) 