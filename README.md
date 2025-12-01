# Anti-Slop MCP Server

A Model Context Protocol (MCP) compliant FastAPI service for detecting and rewriting low-quality or
repetitive AI-generated content ("slop").

## Features

- **Analyze Content**: Score text quality and identify specific issues with generic or verbose AI
  output
- **Improve Content**: Automatically rewrite text to remove fluff and improve clarity
- **Detect AI Phrases**: Flag obvious AI-generated phrases like "delve into", "it's worth noting"
- **Remove Filler Words**: Strip unnecessary words like "actually", "basically", "literally"
- **Detect Clichés**: Find overused corporate buzzwords and tired expressions
- **Remove Hedging**: Eliminate weak language like "perhaps", "maybe", "might"
- **Detect Passive Voice**: Identify and count passive voice usage
- **Normalize Whitespace**: Clean up formatting inconsistencies
- **Calculate Readability**: Get Flesch reading ease scores and grade levels
- **Detect Repetition**: Find repeated phrases within text
- **Detect Run-on Sentences**: Flag overly long sentences
- **Remove Redundancies**: Fix redundant phrases like "past history", "future plans"
- **Format Python Code**: Auto-format Python code with proper indentation using black
- **MCP Compliant**: Follows the Model Context Protocol for easy integration with AI agents

## Installation

```bash
cd anti-slop-mcp
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Running the Server

```bash
python server.py
```

Or with uvicorn directly:

```bash
uvicorn server:app --host 0.0.0.0 --port 3000 --reload
```

The server will start on port 3000 (or the port specified in the `PORT` environment variable).

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`

## API Endpoints

### 1. Analyze Content for Slop

**Endpoint**: `POST /analyze_content_for_slop`

**Request Body**:

```json
{
  "content": "Your text to analyze here..."
}
```

**Response**:

```json
{
  "content": "Original text...",
  "analysis": {
    "score": 7,
    "issues": ["Excessive use of qualifiers", "Generic opening statements"],
    "suggestions": ["Remove phrases like 'it's worth noting'", "Be more specific in your claims"]
  }
}
```

### 2. Remove Em Dashes

**Endpoint**: `POST /remove_em_dashes`

### 3. Remove Emojis

**Endpoint**: `POST /remove_emojis`

### 4. Detect AI Phrases

**Endpoint**: `POST /detect_ai_phrases`

**Response**:

```json
{
  "content": "Original text...",
  "ai_phrases_detected": 3,
  "total_instances": 3,
  "phrases": [
    { "phrase": "it's worth noting", "count": 1, "instances": ["it's worth noting"] },
    { "phrase": "delve into", "count": 1, "instances": ["delve into"] }
  ],
  "slop_score": 6
}
```

### 5. Remove Filler Words

**Endpoint**: `POST /remove_filler_words`

### 6. Detect Clichés

**Endpoint**: `POST /detect_cliches`

### 7. Remove Hedging

**Endpoint**: `POST /remove_hedging`

### 8. Detect Passive Voice

**Endpoint**: `POST /detect_passive_voice`

### 9. Normalize Whitespace

**Endpoint**: `POST /normalize_whitespace`

### 10. Calculate Readability

**Endpoint**: `POST /calculate_readability`

**Response**:

```json
{
  "stats": {
    "sentences": 5,
    "words": 87,
    "syllables": 134,
    "avg_sentence_length": 17.4,
    "avg_syllables_per_word": 1.5
  },
  "readability": {
    "flesch_reading_ease": 65,
    "grade_level": 8.2,
    "difficulty": "Standard"
  }
}
```

### 11. Detect Repetition

**Endpoint**: `POST /detect_repetition`

**Request Body**:

```json
{
  "content": "Your text...",
  "min_length": 3
}
```

### 12. Detect Run-on Sentences

**Endpoint**: `POST /detect_run_on_sentences`

**Request Body**:

```json
{
  "content": "Your text...",
  "max_words": 30
}
```

### 13. Remove Redundancies

**Endpoint**: `POST /remove_redundancies`

### 14. Format Python Code

**Endpoint**: `POST /format_python`

**Request Body**:

```json
{
  "content": "def hello():\nprint('world')"
}
```

**Response**:

```json
{
  "original_content": "def hello():\nprint('world')",
  "formatted_content": "def hello():\n    print('world')\n",
  "changes_made": "Formatted with black (line length: 100)",
  "formatter": "black"
}
```

### 15. Improve Content from Slop

**Endpoint**: `POST /improve_content_from_slop`

**Request Body**:

```json
{
  "content": "Your text to improve here...",
  "preserve_meaning": true,
  "target_tone": "professional"
}
```

## Usage Examples

### Using curl

```bash
# Detect AI phrases
curl -X POST http://localhost:3000/detect_ai_phrases \
 -H "Content-Type: application/json" \
 -d '{"content": "It'\''s worth noting that we need to delve into this robust solution"}'

# Calculate readability
curl -X POST http://localhost:3000/calculate_readability \
 -H "Content-Type: application/json" \
 -d '{"content": "Your content here..."}'

# Improve content
curl -X POST http://localhost:3000/improve_content_from_slop \
 -H "Content-Type: application/json" \
 -d '{"content": "It'\''s worth noting that...", "target_tone": "professional"}'
```

### Using Python

```python
import requests

# Detect AI phrases
response = requests.post(
 "http://localhost:3000/detect_ai_phrases",
 json={"content": "It's worth noting that we should delve into this..."}
)
print(response.json())

# Cleanup pipeline
def cleanup_content(text):
 # Remove filler words
 r = requests.post("http://localhost:3000/remove_filler_words", json={"content": text})
 text = r.json()["cleaned_content"]

 # Remove hedging
 r = requests.post("http://localhost:3000/remove_hedging", json={"content": text})
 text = r.json()["cleaned_content"]

 # Normalize whitespace
 r = requests.post("http://localhost:3000/normalize_whitespace", json={"content": text})
 text = r.json()["normalized_content"]

 return text
```

## ModernizedAI Integration

Create a connector definition for ModernizedAI:

```json
{
  "id": "anti_slop",
  "name": "Anti-Slop MCP",
  "type": "mcp",
  "base_url": "http://localhost:3000",
  "tools": [
    {
      "name": "detect_ai_phrases",
      "endpoint": "/detect_ai_phrases",
      "method": "POST",
      "description": "Detect AI-generated phrases and slop indicators"
    },
    {
      "name": "remove_filler_words",
      "endpoint": "/remove_filler_words",
      "method": "POST",
      "description": "Remove filler words like '', '', ''"
    },
    {
      "name": "calculate_readability",
      "endpoint": "/calculate_readability",
      "method": "POST",
      "description": "Calculate readability scores and metrics"
    },
    {
      "name": "improve_content_from_slop",
      "endpoint": "/improve_content_from_slop",
      "method": "POST",
      "description": "Rewrite text to remove slop and improve clarity"
    }
  ]
}
```

## Git Repository Setup

Initialize this as a separate git repository:

```bash
cd anti-slop-mcp
git init
git add .
git commit -m "Initial commit: Anti-Slop MCP server"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Development

Run with auto-reload:

```bash
uvicorn server:app --reload --port 3000
```

Run tests (add tests in `tests/` directory):

```bash
pytest
```

## License

MIT
