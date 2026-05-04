'''
Perfromed improvement with 
1. Add Error Handling & Retries
    - Add retry logic for failed tool calls
    - Graceful degradation if MCP server fails
    - Timeout handling

2. Implement Streaming Response (st.write_stream())
    - Stream LLM responses instead of waiting for complete answer
    - Real-time tool execution status (like your UI showed "🔨 Using tool")

3. Add Checkpointing/Persistence (SqliteSaver and AsyncSqliteSaver)
    - Save MCP query history to database
    - Cache tool results to avoid redundant API calls
    - Track conversation threads (for multi-turn interactions)

4. Add Human-in-the-Loop (interrupt())
    - Ask user before executing expensive MCP operations
    - Review sensitive document retrieval before sending to LLM
    - Confirm changes before writing back to external systems

5. Add Structured Output Instead of Free Text (with_structured_output(), parser())
    - Parse MCP tool results into typed objects
    - Validate responses before sending to LLM
    - Extract specific fields (citations, confidence scores)

6. Add Tool Visualization (Like Streamlit UI)
    - Print visual indicators: 🔨 Calling get_docs... ✅ Done
    - Show progress for multi-tool workflows
    - Display token usage and timing

7. Add Conditional Routing  (tools_condition and add_conditional_edges)
    - If tool returns no results → try alternative search
    - If context is too long → summarize before sending to LLM
    - Route to different LLM models based on query complexity

8. Add SubGraph Pattern
    - Create reusable subgraph for document retrieval
    - Separate "search → retrieve → answer" into modular components
    - Compose multiple MCP calls in a subgraph

9. Add Configuration Management (thread_id, CONFIG dicts)
    - Store server params in config file
    - Environment-specific settings (dev/prod)
    - Thread-based session management

'''

# What you'd add based on your LangGraph knowledge:

class MCPState(TypedDict):
    query: str
    library: str
    context: str
    answer: str
    tool_calls: Annotated[List[Dict], operator.add]
    retries: int

# Add conditional routing
def should_retry(state: MCPState) -> bool:
    return state['context'] == "" and state['retries'] < 3

# Add checkpointing
checkpointer = SqliteSaver(conn)

# Add streaming callback
async def stream_tool_progress():
    yield {"status": "🔨 Calling MCP tool..."}
    yield {"status": "✅ Tool complete"}

# Add structured output
class SearchResult(BaseModel):
    answer: str
    sources: List[str]
    confidence: float

# What you have in your UI:
status_holder = st.status(f"🔨 Using '{tool_name}'", expanded=True)

# Apply to console:
def print_tool_status(tool_name, status):
    icons = {"start": "🔨", "success": "✅", "error": "❌"}
    print(f"{icons[status]} {tool_name}...")

print_tool_status("get_docs", "start")
result = await session.call_tool(...)
print_tool_status("get_docs", "success")