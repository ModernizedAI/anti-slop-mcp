# Anti-Slop MCP Server

A Model Context Protocol (MCP) server for detecting and rewriting low-quality or repetitive AI-generated content ("slop").

## What is MCP?

MCP (Model Context Protocol) is a standard protocol that allows AI assistants to connect to external tools and data sources. This server implements MCP to provide anti-slop tools that can be used by any MCP-compatible client (like Claude Desktop, IDEs, etc.).

## Features

### Detection Tools
- **Analyze Content**: Score text quality (0-10) and identify specific issues with generic or verbose AI output
- **Detect AI Phrases**: Flag obvious AI-generated phrases like "delve into", "it's worth noting", "in today's world"
- **Detect Clichés**: Find overused corporate buzzwords and tired expressions
- **Detect Passive Voice**: Identify and count passive voice usage
- **Detect Repetition**: Find repeated phrases within text
- **Detect Run-on Sentences**: Flag overly long sentences

### Cleaning Tools
- **Remove Filler Words**: Strip unnecessary words like "actually", "basically", "literally"
- **Remove Hedging**: Eliminate weak language like "perhaps", "maybe", "might"
- **Remove Redundancies**: Fix redundant phrases like "past history", "future plans"
- **Remove Emojis**: Clean emojis from text
- **Normalize Whitespace**: Clean up formatting inconsistencies

### Analysis Tools
- **Calculate Readability**: Get Flesch reading ease scores and grade levels

### AI-Powered Tools
- **Improve Content**: Automatically rewrite text to remove slop and improve clarity (requires OpenAI API key)

## Installation

```bash
cd anti-slop-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

For development with additional tools:
```bash
pip install -e ".[dev]"
```

## Configuration

For AI-powered tools (analyze_content_for_slop, improve_content_from_slop), set your OpenAI API key:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Using with Claude Desktop

Add this to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "anti-slop": {
      "command": "python",
      "args": ["/path/to/anti-slop-mcp/server.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Restart Claude Desktop and the anti-slop tools will be available!

## Using with Other MCP Clients

The server uses stdio transport and follows the MCP specification. Connect to it by running:

```bash
python server.py
```

Then communicate via JSON-RPC 2.0 messages over stdin/stdout.

## Available Tools

### 1. detect_ai_phrases
Detect common AI-generated phrases.

**Input:**
- `content` (string): Text to scan

**Example:**
```json
{
  "content": "Let me delve into this topic. It's worth noting that..."
}
```

### 2. remove_filler_words
Remove filler words to make text more concise.

**Input:**
- `content` (string): Text to clean

### 3. detect_cliches
Find business clichés and buzzwords.

**Input:**
- `content` (string): Text to scan

### 4. remove_hedging
Remove hedging language to make text more direct.

**Input:**
- `content` (string): Text to clean

### 5. detect_passive_voice
Analyze passive voice usage.

**Input:**
- `content` (string): Text to analyze

### 6. calculate_readability
Calculate readability metrics (Flesch score, grade level).

**Input:**
- `content` (string): Text to analyze

### 7. detect_repetition
Find repeated phrases.

**Input:**
- `content` (string): Text to scan
- `min_length` (integer, optional): Minimum phrase length (default: 3)

### 8. detect_run_on_sentences
Detect overly long sentences.

**Input:**
- `content` (string): Text to analyze
- `max_words` (integer, optional): Maximum words per sentence (default: 30)

### 9. remove_redundancies
Remove redundant phrases.

**Input:**
- `content` (string): Text to clean

### 10. remove_emojis
Remove all emojis from text.

**Input:**
- `content` (string): Text to clean

### 11. normalize_whitespace
Normalize whitespace and formatting.

**Input:**
- `content` (string): Text to normalize

### 12. analyze_content_for_slop ⚡ (Requires OpenAI API Key)
Analyze text for slop using AI.

**Input:**
- `content` (string): Text to analyze

### 13. improve_content_from_slop ⚡ (Requires OpenAI API Key)
Rewrite text to remove slop using AI.

**Input:**
- `content` (string): Text to improve
- `preserve_meaning` (boolean, optional): Preserve original meaning (default: true)
- `target_tone` (string, optional): Target tone (default: "professional")

## Testing the Server

Test with JSON-RPC messages:

```bash
# Initialize
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | python server.py

# List tools
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}') | python server.py

# Call a tool
cat << 'EOF' | python server.py
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "detect_ai_phrases", "arguments": {"content": "Let me delve into this topic..."}}}
EOF
```

## Development

The package is built with modern Python packaging standards:
- `pyproject.toml` - Modern Python packaging configuration
- `mcp` - Official Model Context Protocol Python SDK
- `openai` - For AI-powered analysis and improvement tools
- `pydantic` - For data validation

## Architecture

This is a **stdio-based MCP server**, meaning:
- It communicates via standard input/output (stdin/stdout)
- It uses JSON-RPC 2.0 protocol
- It's designed to be spawned as a subprocess by MCP clients
- It's NOT a REST API or HTTP server

The old FastAPI version has been saved as `server_old.py` for reference.

## License

MIT
