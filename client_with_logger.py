import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils import get_response_from_llm

load_dotenv()

# Configure logging - simplified without Unicode characters
logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to INFO to reduce verbosity
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'client_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress verbose HTTPX and Groq logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("groq").setLevel(logging.WARNING)

logger.info("Client starting - SERPER_API_KEY: Set" if os.getenv("SERPER_API_KEY") else "Client starting - SERPER_API_KEY: NOT SET")

SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "mcp_server.py"],
    env=None
)

async def main():
    logger.info("Connecting to MCP server...")
    
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # List available tools
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            logger.info(f"Available tools: {tool_names}")
            print("Available tools:", tool_names)
            
            # Using a tool
            query = "how to publish a package with uv on github?"
            library = "langchain"
            
            logger.info(f"Calling get_docs with query='{query}', library='{library}'")
            result = await session.call_tool(
                "get_docs",
                arguments={"query": query, "library": library}
            )
            
            # Extract text content from result
            context = result.content[0].text if result.content else "No context"
            logger.info(f"Retrieved context length: {len(context)} characters")
            
            user_prompt_with_context = f"Query: {query}, Context: {context}"
            
            # LLM function
            SYSTEM_PROMPT = """
            Answer ONLY using the provided context. If info is missing say you don't know.
            Keep every 'SOURCE:' line exactly; list sources at the end.
            """
            
            logger.info("Calling LLM...")
            answer = get_response_from_llm(
                user_prompt=user_prompt_with_context, 
                system_prompt=SYSTEM_PROMPT, 
                model="llama-3.3-70b-versatile"
            )
            
            print("\n" + "="*60)
            print("ANSWER:")
            print("="*60)
            print(answer)
            print("="*60)
            
            logger.info("Client completed successfully")

if __name__ == "__main__":
    asyncio.run(main())