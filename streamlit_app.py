import asyncio
import streamlit as st
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import os
from dotenv import load_dotenv
from utils import get_response_from_llm

load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Documentation Assistant",
    page_icon="📚",
    layout="wide"
)

# Define the async function FIRST (before using it)
async def get_documentation_answer(query: str, library: str, model: str) -> str:
    """Get answer from documentation using MCP server"""
    
    SERVER_PARAMS = StdioServerParameters(
        command="uv",
        args=["run", "mcp_server.py"],
        env=None
    )
    
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Call the get_docs tool
            result = await session.call_tool(
                "get_docs",
                arguments={"query": query, "library": library}
            )
            
            # Extract context from result
            if result.content and len(result.content) > 0:
                context = result.content[0].text
            else:
                return "No documentation found for your query."
            
            # Create prompt for LLM
            user_prompt_with_context = f"Query: {query}\n\nContext: {context}"
            
            SYSTEM_PROMPT = """
            Answer ONLY using the provided context. If information is missing, say you don't know.
            Keep every 'SOURCE:' line exactly as they appear; list all sources at the end.
            Format your answer in clear paragraphs with bullet points where appropriate.
            """
            
            # Get LLM response
            answer = get_response_from_llm(
                user_prompt=user_prompt_with_context, 
                system_prompt=SYSTEM_PROMPT, 
                model=model
            )
            
            return answer
        
# Title and description
st.title("📚 AI Documentation Assistant")
st.markdown("Search and get answers from official documentation of LangChain, LlamaIndex, OpenAI, and UV")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Library selection
    library = st.selectbox(
        "Select Library",
        options=["langchain", "llama-index", "openai", "uv"],
        format_func=lambda x: x.title()
    )
    
    # Model selection
    model = st.selectbox(
        "Select LLM Model",
        options=["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
        help="Choose the Groq model for generating answers"
    )
    
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This app uses:
    - **MCP (Model Context Protocol)** for tool integration
    - **Serper API** for web search
    - **Groq** for LLM processing
    """)

# Main chat interface
st.header("💬 Ask a Question")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(f"Ask something about {library}..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(f"Searching {library} documentation and generating answer..."):
            try:
                # Run the async function
                response = asyncio.run(
                    get_documentation_answer(
                        query=prompt, 
                        library=library, 
                        model=model
                    )
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Display example queries
with st.sidebar.expander("💡 Example Queries"):
    st.markdown("""
    - How to create a vector store with LangChain?
    - How to publish a package with uv?
    - How to use embeddings with OpenAI?
    - How to build a RAG pipeline with LlamaIndex?
    """)

# Async function to get answer from MCP server
async def get_documentation_answer(query: str, library: str, model: str) -> str:
    """Get answer from documentation using MCP server"""
    
    SERVER_PARAMS = StdioServerParameters(
        command="uv",
        args=["run", "mcp_server.py"],
        env=None
    )
    
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Call the get_docs tool
            result = await session.call_tool(
                "get_docs",
                arguments={"query": query, "library": library}
            )
            
            # Extract context from result
            if result.content and len(result.content) > 0:
                context = result.content[0].text
            else:
                return "No documentation found for your query."
            
            # Create prompt for LLM
            user_prompt_with_context = f"Query: {query}\n\nContext: {context}"
            
            SYSTEM_PROMPT = """
            Answer ONLY using the provided context. If information is missing, say you don't know.
            Keep every 'SOURCE:' line exactly as they appear; list all sources at the end.
            Format your answer in clear paragraphs with bullet points where appropriate.
            """
            
            # Get LLM response
            answer = get_response_from_llm(
                user_prompt=user_prompt_with_context, 
                system_prompt=SYSTEM_PROMPT, 
                model=model
            )
            
            return answer