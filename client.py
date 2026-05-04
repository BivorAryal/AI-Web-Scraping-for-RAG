import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from groq import Groq
import os
from dotenv import load_dotenv
from utils import get_response_from_llm

load_dotenv()

#1. connection
SERVER_PARAMS = StdioServerParameters(
    command= "uv",
    args = ["run", "mcp_server.py"],
    env = None
    )

async def main():
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):  # build Client
        async with ClientSession(read_stream, write_stream) as session:     # Client Session
            await session.initialize()                                      # initialized

            # List available tools
            tools_response = await session.list_tools()
            print("Available tools:", [t.name for t in tools_response.tools])

            # Using a tool
            query = "how to publish a package with uv on github?"
            library = "langchain"

            result = await session.call_tool(
                "get_docs",
                arguments = {"query": query, "library": library}
            )
            context = result.content
            user_prompt_with_context = f"Query: {query}, Context{context}"

            # LLM function
            SYSTEM_PROMPT= """
            Answer ONLY using the provided context. If info is missing say you don't know.
            Keep every 'SOURCE:' line exactly; list sources at the end.
            """
            answer = get_response_from_llm(user_prompt=user_prompt_with_context, system_prompt=SYSTEM_PROMPT, model="llama-3.3-70b-versatile")
            print("ANSWER: ", answer)
                                                          
if __name__ == "__main__":
    asyncio.run(main())

