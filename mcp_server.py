# Create AI web scrapping tool
# Steps 1: Search Web
# Steps 2: Open official docs
# Steps 3: Read documentation and write code accordingly


import json
import os
from dotenv import load_dotenv
import httpx
# import asyncio
import sys

from utils import clean_html_to_txt
from fastmcp import FastMCP

load_dotenv()
mcp = FastMCP("docs")


# Steps 1: Search Web: we get lots of sources in Internet (using serper refine it)
SERPER_URL = "https://google.serper.dev/search"
async def search_web(query: str) -> dict | None:
    """Search the web using Serper API"""
    payload = json.dumps({"q":query, "num": 2 })
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SERPER_URL, 
            headers=headers, 
            data=payload, 
            timeout = 30.0
        )
        response.raise_for_status()
        return response.json()
            
# Steps 2: Open official docs
async def fetch_url(url:str):
    """    Fetch and clean HTML content from a URL  """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            cleaned_response = clean_html_to_txt(response.text)
            return cleaned_response
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Steps 3: Read documentation and write code accordingly
#official docs
docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
    "uv": "docs.astral.sh/uv",
}
@mcp.tool()
async def get_docs(query:str, library:str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, llama-index and uv.

    Args:
        query: The query to search for (e.g. "Publish a package with UV")
        library: The library to search in (e.g. "uv")

    Returns:
        Summarized text from the docs with source links.
    """

    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")

    query = f"{docs_urls[library]} {query}"
    results = await search_web(query)

    if not results or len(results.get("organic", [])) == 0:
        return "No result found"
    
    text_parts = []
    for result in results['organic']:
        link = result.get("link", "")
        if link:
            raw = await fetch_url(link)
            if raw:
                labeled = f"SOURCE: {link}\n{raw}"
                text_parts.append(labeled)
    
    return "\n\n".join(text_parts) if text_parts else "No content extracted"

def main():
    """Run the MCP server"""
    mcp.run(transport = "stdio")

if __name__ == "__main__":
    main()