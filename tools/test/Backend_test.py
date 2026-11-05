import sys
from pathlib import Path

# Add project root ("D:\New folder") to Python's search path before importing backend
sys.path.append(str(Path(__file__).resolve().parents[2]))  # or parents[1] depending on execution
if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend import run_travel_agent

user_input = input("enter travel Request: ")
res = run_travel_agent(
    user_input=user_input,
    thread_id="test_user"
)
print(res["answer"])
