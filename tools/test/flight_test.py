import sys
from pathlib import Path

# Adds "D:\New folder" to Python's search path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from tools.flight_tool import search_flights

res = search_flights("plans a chennai  trip from goa")
print(res)
