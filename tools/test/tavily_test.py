import sys
from pathlib import Path

# Adds "D:\New folder" to Python's search path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from tools.tavily_tool import tavily_search

res = tavily_search("Best Hotels in India")
print(res)
