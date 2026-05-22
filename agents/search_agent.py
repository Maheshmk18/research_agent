from dotenv import load_dotenv
from tavily import TavilyClient
import os


load_dotenv()


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def run_search(topic: str):
    query = f"{topic} latest research"
    result = tavily_client.search(query=query, max_results=5)

    sources = []
    for item in result.get("results", []):
        sources.append(
            {
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
        )

    return {"query": query, "sources": sources}
