#!/usr/bin/env python3
"""MCP server for anti-slop tools."""
import asyncio
import os
import logging
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from anti_slop import ToolRegistry
from anti_slop.formatters import TextFormatter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anti-slop-mcp")

server = Server("anti-slop-mcp")
registry = ToolRegistry(openai_api_key=os.getenv("OPENAI_API_KEY"))
formatter = TextFormatter()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools."""
    tools = []
    for tool in registry.list_tools():
        tools.append(types.Tool(
            name=tool.name,
            description=tool.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to process"}
                },
                "required": ["content"]
            }
        ))
    return tools


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute a tool."""
    if not arguments:
        return [types.TextContent(
            type="text",
            text="Error: Missing arguments"
        )]
    
    result = registry.execute_tool(name, **arguments)
    formatted_text = formatter.format(result)
    
    return [types.TextContent(
        type="text",
        text=formatted_text
    )]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="anti-slop-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
