# Anti-Slop Architecture

## Overview

Clean, object-oriented architecture where **the same core logic** is used by both MCP and API servers.

```
anti_slop/
├── base.py              # Base classes (BaseTool, ToolResult)
├── enums.py             # ToolName enum (all tool names)
├── analyzers.py         # Detection tools (AI phrases, clichés, etc.)
├── cleaners.py          # Cleaning tools (filler words, hedging, etc.)
├── ai_tools.py          # AI-powered tools (analyzer, improver)
├── registry.py          # Tool registry (manages all tools)
└── formatters.py        # Output formatters (Text, JSON)
```

## Core Components

### 1. **ToolName Enum** (enums.py)
Type-safe enum for all tool names:
```python
from anti_slop import ToolName

# Use enums (recommended)
registry.execute_tool(ToolName.DETECT_AI_PHRASES, content="...")

# Or strings (still works)
registry.execute_tool("detect_ai_phrases", content="...")

# List all tools
ToolName.list_all()  # Returns all tool name strings

# Validate tool name
ToolName.is_valid("detect_ai_phrases")  # True
```

### 2. **BaseTool** (base.py)
Abstract base class for all tools. Every tool implements:
- `name` - Tool identifier (returns ToolName enum value)
- `description` - What the tool does
- `execute(**kwargs)` - Main logic, returns `ToolResult`

### 3. **ToolResult** (base.py)
Standard result format:
```python
ToolResult(
    success: bool,
    data: Dict[str, Any],
    error: str | None
)
```

### 4. **Tool Categories**

**Analyzers** (analyzers.py):
- `AIPhrasesAnalyzer` - Detect AI-generated phrases
- `ClicheAnalyzer` - Detect business buzzwords
- `PassiveVoiceAnalyzer` - Detect passive voice
- `ReadabilityAnalyzer` - Calculate Flesch scores
- `RepetitionAnalyzer` - Find repeated phrases
- `RunOnSentenceAnalyzer` - Detect long sentences

**Cleaners** (cleaners.py):
- `FillerWordsCleaner` - Remove "actually", "basically", etc.
- `HedgingCleaner` - Remove "perhaps", "maybe", etc.
- `RedundancyCleaner` - Remove "past history", etc.
- `EmojiCleaner` - Remove emojis
- `WhitespaceCleaner` - Normalize spacing

**AI Tools** (ai_tools.py):
- `ContentAnalyzer` - AI-powered slop analysis
- `ContentImprover` - AI-powered content rewriting

### 5. **ToolRegistry** (registry.py)
Central registry that:
- Registers all tools on initialization
- Provides `execute_tool(name: str | ToolName, **kwargs)` method
- Validates tool names using ToolName enum
- Used by both MCP and API servers

### 6. **Formatters** (formatters.py)
Convert `ToolResult` to different output formats:
- `TextFormatter` - Human-readable text (for MCP)
- `JSONFormatter` - JSON format (for API)

## Servers

### MCP Server (mcp_server.py)
```python
registry = ToolRegistry(openai_api_key=os.getenv("OPENAI_API_KEY"))
formatter = TextFormatter()

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):
    result = registry.execute_tool(name, **arguments)
    formatted_text = formatter.format(result)
    return [types.TextContent(type="text", text=formatted_text)]
```

### API Server (api_server.py)
```python
registry = ToolRegistry(openai_api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/execute/{tool_name}")
async def execute_tool(tool_name: str, request: ToolRequest):
    result = registry.execute_tool(tool_name, **request.dict())
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return JSONResponse(content=result.data)
```

## Benefits

✅ **Single Source of Truth**: Tool logic is in one place  
✅ **Type Safety**: Enums prevent typos in tool names  
✅ **Easy Testing**: Test tools independently of servers  
✅ **Extensibility**: Add new tools by creating a class  
✅ **Consistency**: Same results from MCP and API  
✅ **Clean Separation**: Tools, formatting, and transport are separate  
✅ **Auto-complete**: IDE suggestions for tool names  

## Adding a New Tool

1. Add enum value to `ToolName` in `enums.py`
2. Create a class inheriting from `BaseTool`
3. Implement `name` (return enum value), `description`, and `execute()`
4. Register it in `ToolRegistry._register_tools()`
5. Add formatter support in `TextFormatter` if needed
6. Both servers automatically expose it!

Example:
```python
# 1. Add to enums.py
class ToolName(str, Enum):
    MY_NEW_TOOL = "my_new_tool"
    # ... other tools

# 2. Create tool class
class MyNewTool(BaseTool):
    @property
    def name(self) -> str:
        return ToolName.MY_NEW_TOOL.value
    
    @property
    def description(self) -> str:
        return "Does something cool"
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        result = do_something(content)
        return ToolResult(
            success=True,
            data={"result": result}
        )
```

## Running the Servers

### MCP Server (for Claude Desktop, etc.)
```bash
python mcp_server.py
```

Or using the installed script:
```bash
anti-slop-mcp
```

### API Server (REST API)
```bash
python api_server.py
```

Or using the installed script:
```bash
anti-slop-api
```

Or with uvicorn:
```bash
uvicorn api_server:app --host 0.0.0.0 --port 3000
```

## Development

Install with dev dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black .
ruff check .
```

## Old Files

- `server.py` → Replaced by `mcp_server.py` (cleaner OOP version)
- `server_old.py` → Original FastAPI server (kept for reference)
