from tavily import TavilyClient
import os 

from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(
    api_key= os.getenv("TRAVILY_API_KEY")
)

def tavily_search(query):
    res = client.search(
        query=query,
        max_results=5
    )

    result = []
    for i, r in enumerate(res["results"], 1):
          title = r.get("title","Unknown")
          url = r.get("url")
          snippet = r.get("content" , "").strip()

          if len(snippet) > 300:
               snippet = snippet[:300].rsplit(" ",1)[0] + "..."
          result.append(f"{i}. **{title}**\n {url}\n {snippet}")

    return "\n\n".join(result)