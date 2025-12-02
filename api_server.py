#!/usr/bin/env python3
"""FastAPI server for anti-slop tools."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from anti_slop import ToolRegistry, ToolName

app = FastAPI(
    title="Anti-Slop API",
    description="API for detecting and cleaning low-quality AI-generated content",
    version="1.0.0"
)

registry = ToolRegistry(openai_api_key=os.getenv("OPENAI_API_KEY"))


class ToolRequest(BaseModel):
    """Generic request for tool execution."""
    content: str = Field(..., description="The text to process")
    min_length: Optional[int] = Field(3, description="Minimum phrase length for repetition detection")
    max_words: Optional[int] = Field(30, description="Maximum words per sentence for run-on detection")
    preserve_meaning: Optional[bool] = Field(True, description="Preserve original meaning when improving")
    target_tone: Optional[str] = Field("professional", description="Target tone for content improvement")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Anti-Slop API",
        "version": "1.0.0",
        "tools": [tool.name for tool in registry.list_tools()]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "anti-slop-api"}


@app.get("/tools")
async def list_tools():
    """List all available tools."""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "enum_value": tool.name
            }
            for tool in registry.list_tools()
        ],
        "tool_names": ToolName.list_all()
    }


@app.post("/execute/{tool_name}")
async def execute_tool(tool_name: ToolName, request: ToolRequest):
    """Execute a specific tool."""
    result = registry.execute_tool(
        tool_name,
        content=request.content,
        min_length=request.min_length,
        max_words=request.max_words,
        preserve_meaning=request.preserve_meaning,
        target_tone=request.target_tone,
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return JSONResponse(content=result.data)


# Convenience endpoints for each tool
@app.post(f"/{ToolName.DETECT_AI_PHRASES.value}")
async def detect_ai_phrases(request: ToolRequest):
    """Detect AI-generated phrases."""
    return await execute_tool(ToolName.DETECT_AI_PHRASES, request)


@app.post(f"/{ToolName.REMOVE_FILLER_WORDS.value}")
async def remove_filler_words(request: ToolRequest):
    """Remove filler words."""
    return await execute_tool(ToolName.REMOVE_FILLER_WORDS, request)


@app.post(f"/{ToolName.DETECT_CLICHES.value}")
async def detect_cliches(request: ToolRequest):
    """Detect clichés."""
    return await execute_tool(ToolName.DETECT_CLICHES, request)


@app.post(f"/{ToolName.REMOVE_HEDGING.value}")
async def remove_hedging(request: ToolRequest):
    """Remove hedging language."""
    return await execute_tool(ToolName.REMOVE_HEDGING, request)


@app.post(f"/{ToolName.DETECT_PASSIVE_VOICE.value}")
async def detect_passive_voice(request: ToolRequest):
    """Detect passive voice."""
    return await execute_tool(ToolName.DETECT_PASSIVE_VOICE, request)


@app.post(f"/{ToolName.CALCULATE_READABILITY.value}")
async def calculate_readability(request: ToolRequest):
    """Calculate readability metrics."""
    return await execute_tool(ToolName.CALCULATE_READABILITY, request)


@app.post(f"/{ToolName.DETECT_REPETITION.value}")
async def detect_repetition(request: ToolRequest):
    """Detect repeated phrases."""
    return await execute_tool(ToolName.DETECT_REPETITION, request)


@app.post(f"/{ToolName.DETECT_RUN_ON_SENTENCES.value}")
async def detect_run_on_sentences(request: ToolRequest):
    """Detect run-on sentences."""
    return await execute_tool(ToolName.DETECT_RUN_ON_SENTENCES, request)


@app.post(f"/{ToolName.REMOVE_REDUNDANCIES.value}")
async def remove_redundancies(request: ToolRequest):
    """Remove redundant phrases."""
    return await execute_tool(ToolName.REMOVE_REDUNDANCIES, request)


@app.post(f"/{ToolName.REMOVE_EMOJIS.value}")
async def remove_emojis(request: ToolRequest):
    """Remove emojis."""
    return await execute_tool(ToolName.REMOVE_EMOJIS, request)


@app.post(f"/{ToolName.NORMALIZE_WHITESPACE.value}")
async def normalize_whitespace(request: ToolRequest):
    """Normalize whitespace."""
    return await execute_tool(ToolName.NORMALIZE_WHITESPACE, request)


@app.post(f"/{ToolName.ANALYZE_CONTENT_FOR_SLOP.value}")
async def analyze_content_for_slop(request: ToolRequest):
    """Analyze content for slop using AI."""
    return await execute_tool(ToolName.ANALYZE_CONTENT_FOR_SLOP, request)


@app.post(f"/{ToolName.IMPROVE_CONTENT_FROM_SLOP.value}")
async def improve_content_from_slop(request: ToolRequest):
    """Improve content using AI."""
    return await execute_tool(ToolName.IMPROVE_CONTENT_FROM_SLOP, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
