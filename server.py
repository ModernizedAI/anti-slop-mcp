import asyncio
import re
import os
import logging
from typing import Optional
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anti-slop-mcp")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

server = Server("anti-slop-mcp")

def count_syllables(word: str) -> int:
    word = re.sub(r'[^a-z]', '', word.lower())
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = re.findall(r'[aeiouy]{1,2}', word)
    return len(syllables) if syllables else 1

def get_reading_difficulty(flesch_score: float) -> str:
    if flesch_score >= 90:
        return 'Very Easy'
    elif flesch_score >= 80:
        return 'Easy'
    elif flesch_score >= 70:
        return 'Fairly Easy'
    elif flesch_score >= 60:
        return 'Standard'
    elif flesch_score >= 50:
        return 'Fairly Difficult'
    elif flesch_score >= 30:
        return 'Difficult'
    return 'Very Difficult'

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_content_for_slop",
            description="Analyze text for low-quality AI-generated content. Returns a score (0-10) where higher means more slop, plus specific issues and suggestions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to analyze"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="detect_ai_phrases",
            description="Detect common AI-generated phrases like 'delve into', 'it's worth noting', 'in today's world', etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to scan for AI phrases"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="remove_filler_words",
            description="Remove filler words like 'actually', 'basically', 'literally', 'just', 'very', 'really', etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to clean"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="detect_cliches",
            description="Detect business clichés and buzzwords like 'game changer', 'synergy', 'low-hanging fruit', etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to scan for clichés"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="remove_hedging",
            description="Remove hedging language like 'perhaps', 'maybe', 'might', 'it seems', etc. to make text more direct.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to clean"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="detect_passive_voice",
            description="Detect passive voice usage in text and calculate percentage of passive sentences.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to analyze"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="calculate_readability",
            description="Calculate Flesch reading ease score, grade level, and other readability metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to analyze"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="detect_repetition",
            description="Find repeated phrases in text (helps identify redundant content).",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to scan"},
                    "min_length": {"type": "integer", "description": "Minimum phrase length to detect (default: 3)", "default": 3}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="detect_run_on_sentences",
            description="Detect overly long run-on sentences that should be split.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to analyze"},
                    "max_words": {"type": "integer", "description": "Maximum words per sentence (default: 30)", "default": 30}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="remove_redundancies",
            description="Remove redundant phrases like 'past history', 'future plans', 'absolutely essential', etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to clean"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="improve_content_from_slop",
            description="Use AI to rewrite text, removing slop and improving clarity while preserving meaning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to improve"},
                    "preserve_meaning": {"type": "boolean", "description": "Preserve original meaning (default: true)", "default": True},
                    "target_tone": {"type": "string", "description": "Target tone (default: 'professional')", "default": "professional"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="remove_emojis",
            description="Remove all emojis from text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to clean"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="normalize_whitespace",
            description="Normalize whitespace, removing extra spaces, tabs, and blank lines.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text to normalize"}
                },
                "required": ["content"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    
    if not arguments:
        raise ValueError("Missing arguments")
    
    content = arguments.get("content", "")
    
    if name == "analyze_content_for_slop":
        if not client:
            return [types.TextContent(type="text", text="Error: OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")]
        
        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a content quality analyzer. Analyze the given text for "slop" - low-quality, repetitive, generic, or unnecessarily verbose AI-generated content. 
                        
Rate the content on a scale of 0-10 where:
- 0-3: High quality, concise, specific content
- 4-6: Moderate quality with some generic phrases
- 7-10: Low quality "slop" with excessive fluff, repetition, or generic statements

Provide a JSON response with:
- score (0-10)
- issues (array of specific problems found)
- suggestions (array of improvement recommendations)"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this content:\n\n{content}"
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(completion.choices[0].message.content)
            
            result = f"""Analysis Results:
Score: {analysis.get('score', 0)}/10

Issues Found:
{chr(10).join('- ' + issue for issue in analysis.get('issues', []))}

Suggestions:
{chr(10).join('- ' + suggestion for suggestion in analysis.get('suggestions', []))}"""
            
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error analyzing content: {str(e)}")]
    
    elif name == "detect_ai_phrases":
        ai_phrases = [
            'delve into', 'delve deeper', 'delving into',
            "it's worth noting", 'worth noting that',
            "in today's world", "in today's landscape", "in today's digital age",
            'navigate the complexities', 'navigating the complexities',
            'at the end of the day',
            "it's important to note",
            'plays a crucial role',
            'robust solution', 'robust framework',
            'holistic approach', 'holistic view',
            'leverage', 'leveraging',
            'synergy', 'synergistic',
            'paradigm shift',
            'game changer', 'game-changer',
            'disrupt', 'disruptive',
            'cutting-edge', 'cutting edge',
            'state-of-the-art', 'state of the art',
            'best practices',
            'deep dive', 'deep-dive',
            'unpack', "let's unpack",
            'double down',
            'circle back',
            'move the needle',
            'low-hanging fruit',
            'on the same page',
            'think outside the box',
            'push the envelope',
            'touch base'
        ]
        
        found = []
        for phrase in ai_phrases:
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found.append(f"'{phrase}' - found {len(matches)} time(s)")
        
        slop_score = min(10, len(found) * 2)
        
        if found:
            result = f"AI Phrases Detected: {len(found)}\nSlop Score: {slop_score}/10\n\n" + "\n".join(found)
        else:
            result = "No AI phrases detected. Content looks clean!"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "remove_filler_words":
        filler_words = ['actually', 'basically', 'literally', 'just', 'very', 'really', 'quite', 'rather', 'somewhat', 'perhaps', 'maybe']
        found = {}
        cleaned = content
        
        for word in filler_words:
            pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found[word] = len(matches)
                cleaned = pattern.sub('', cleaned)
        
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned).strip()
        
        result = f"Cleaned Content:\n{cleaned}\n\nRemoved {sum(found.values())} filler words"
        if found:
            result += ":\n" + "\n".join(f"- {word}: {count}" for word, count in found.items())
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "detect_cliches":
        cliches = [
            'at the end of the day', 'think outside the box', 'game changer',
            'low-hanging fruit', 'move the needle', 'paradigm shift',
            'synergy', 'win-win', 'touch base', 'circle back',
            'take it to the next level', 'best of breed', 'industry leading',
            'world class', 'bleeding edge', 'mission critical',
            'seamless integration', 'turnkey solution', 'value add',
            'best in class', 'drill down', 'bandwidth',
            'actionable insights', 'core competency'
        ]
        
        found = []
        for cliche in cliches:
            pattern = re.compile(r'\b' + re.escape(cliche) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found.append(f"'{cliche}' - {len(matches)} time(s)")
        
        if found:
            result = f"Clichés Detected: {len(found)}\n\n" + "\n".join(found)
        else:
            result = "No clichés detected!"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "remove_hedging":
        hedge_phrases = [
            'it seems', 'it appears', 'it might be', 'it could be',
            'perhaps', 'maybe', 'possibly', 'probably',
            'might', 'could', 'may', 'would seem',
            'in some ways', 'to some extent', 'sort of', 'kind of',
            'I think', 'I believe', 'I feel',
            'somewhat', 'fairly', 'relatively',
            'could potentially', 'might possibly'
        ]
        
        found = {}
        cleaned = content
        
        for phrase in hedge_phrases:
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found[phrase] = len(matches)
                cleaned = pattern.sub('', cleaned)
        
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned).strip()
        
        result = f"Cleaned Content:\n{cleaned}\n\nRemoved {sum(found.values())} hedging phrases"
        if found:
            result += ":\n" + "\n".join(f"- '{phrase}': {count}" for phrase, count in found.items())
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "detect_passive_voice":
        passive_patterns = [
            re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE),
            re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+en\b', re.IGNORECASE)
        ]
        
        matches = []
        for pattern in passive_patterns:
            found = pattern.findall(content)
            matches.extend(found)
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        passive_sentences = [s for s in sentences if any(p.search(s) for p in passive_patterns)]
        
        percentage = round((len(passive_sentences) / len(sentences)) * 100) if sentences else 0
        
        result = f"""Passive Voice Analysis:
Total Sentences: {len(sentences)}
Passive Sentences: {len(passive_sentences)} ({percentage}%)
Passive Phrases Found: {len(matches)}

Recommendation: {"Consider rewriting in active voice" if percentage > 20 else "Passive voice usage is acceptable"}"""
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "calculate_readability":
        sentences = len([s for s in re.split(r'[.!?]+', content) if s.strip()])
        words_list = [w for w in content.split() if w.strip()]
        words = len(words_list)
        syllables = sum(count_syllables(word) for word in words_list)
        
        avg_sentence_length = words / sentences if sentences > 0 else 0
        avg_syllables_per_word = syllables / words if words > 0 else 0
        
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))
        grade_level = max(0, 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59)
        
        result = f"""Readability Analysis:
Flesch Reading Ease: {round(flesch_score)}/100
Difficulty: {get_reading_difficulty(flesch_score)}
Grade Level: {round(grade_level, 1)}

Statistics:
- Sentences: {sentences}
- Words: {words}
- Syllables: {syllables}
- Avg Sentence Length: {round(avg_sentence_length, 1)} words
- Avg Syllables per Word: {round(avg_syllables_per_word, 1)}"""
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "detect_repetition":
        min_length = arguments.get("min_length", 3)
        words = [w.lower() for w in content.split() if w.strip()]
        phrases = {}
        
        for length in range(min_length, 6):
            for i in range(len(words) - length + 1):
                phrase = ' '.join(words[i:i + length])
                phrases[phrase] = phrases.get(phrase, 0) + 1
        
        repeated = [
            (phrase, count)
            for phrase, count in phrases.items()
            if count > 1
        ]
        repeated.sort(key=lambda x: x[1], reverse=True)
        repeated = repeated[:20]
        
        if repeated:
            result = f"Repeated Phrases Found: {len(repeated)}\n\n" + "\n".join(
                f"'{phrase}' - {count} times" for phrase, count in repeated
            )
        else:
            result = "No significant repetition detected."
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "detect_run_on_sentences":
        max_words = arguments.get("max_words", 30)
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        run_on_sentences = [
            (sentence, len(sentence.split()))
            for sentence in sentences
            if len(sentence.split()) > max_words
        ]
        
        percentage = round((len(run_on_sentences) / len(sentences)) * 100) if sentences else 0
        
        result = f"""Run-on Sentence Analysis:
Total Sentences: {len(sentences)}
Run-on Sentences: {len(run_on_sentences)} ({percentage}%)
Threshold: {max_words} words

"""
        if run_on_sentences:
            result += "Run-on sentences found:\n" + "\n".join(
                f"- {word_count} words: {sentence[:100]}..." for sentence, word_count in run_on_sentences[:5]
            )
        else:
            result += "No run-on sentences detected!"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "remove_redundancies":
        redundancies = [
            {'phrase': 'absolutely essential', 'replacement': 'essential'},
            {'phrase': 'absolutely necessary', 'replacement': 'necessary'},
            {'phrase': 'added bonus', 'replacement': 'bonus'},
            {'phrase': 'advance planning', 'replacement': 'planning'},
            {'phrase': 'already existing', 'replacement': 'existing'},
            {'phrase': 'basic fundamentals', 'replacement': 'fundamentals'},
            {'phrase': 'close proximity', 'replacement': 'proximity'},
            {'phrase': 'completely eliminate', 'replacement': 'eliminate'},
            {'phrase': 'end result', 'replacement': 'result'},
            {'phrase': 'final outcome', 'replacement': 'outcome'},
            {'phrase': 'free gift', 'replacement': 'gift'},
            {'phrase': 'future plans', 'replacement': 'plans'},
            {'phrase': 'past history', 'replacement': 'history'},
            {'phrase': 'personal opinion', 'replacement': 'opinion'},
            {'phrase': 'true fact', 'replacement': 'fact'},
            {'phrase': 'unexpected surprise', 'replacement': 'surprise'}
        ]
        
        cleaned = content
        found = []
        
        for item in redundancies:
            pattern = re.compile(r'\b' + re.escape(item['phrase']) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found.append(f"'{item['phrase']}' → '{item['replacement']}' ({len(matches)} times)")
                cleaned = pattern.sub(item['replacement'], cleaned)
        
        result = f"Cleaned Content:\n{cleaned}\n\n"
        if found:
            result += f"Removed {len(found)} redundancies:\n" + "\n".join(found)
        else:
            result += "No redundancies found!"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "improve_content_from_slop":
        if not client:
            return [types.TextContent(type="text", text="Error: OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")]
        
        preserve_meaning = arguments.get("preserve_meaning", True)
        target_tone = arguments.get("target_tone", "professional")
        
        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a content improvement specialist. Rewrite the given text to remove "slop" while {'preserving the original meaning' if preserve_meaning else 'focusing on clarity'}. 

Remove:
- Unnecessary qualifiers and hedging language
- Generic phrases and clichés
- Repetitive statements
- Excessive verbosity
- Overused AI phrases like "delve into", "it's worth noting", "in today's world"

Make the content:
- Concise and direct
- Specific and concrete
- {target_tone} in tone
- More impactful

Return a JSON response with:
- improved_content (the rewritten text)
- changes_made (array describing what was improved)
- original_word_count
- new_word_count"""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this content:\n\n{content}"
                    }
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            import json
            result_data = json.loads(completion.choices[0].message.content)
            
            result = f"""Improved Content:
{result_data.get('improved_content', content)}

Changes Made:
{chr(10).join('- ' + change for change in result_data.get('changes_made', []))}

Word Count: {result_data.get('original_word_count', 0)} → {result_data.get('new_word_count', 0)}"""
            
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error improving content: {str(e)}")]
    
    elif name == "remove_emojis":
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002600-\U000026FF"
            "\U00002700-\U000027BF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE
        )
        
        emojis = emoji_pattern.findall(content)
        cleaned = emoji_pattern.sub('', content)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        result = f"Cleaned Content:\n{cleaned}\n\nRemoved {len(emojis)} emoji(s)"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "normalize_whitespace":
        normalized = content
        normalized = normalized.replace('\t', ' ')
        normalized = re.sub(r' +', ' ', normalized)
        normalized = re.sub(r'\n\n+', '\n\n', normalized)
        normalized = normalized.replace('\r\n', '\n')
        normalized = normalized.strip()
        
        chars_removed = len(content) - len(normalized)
        
        result = f"Normalized Content:\n{normalized}\n\nRemoved {chars_removed} extra whitespace character(s)"
        
        return [types.TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
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
