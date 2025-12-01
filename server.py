from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import re
import os
from openai import OpenAI

app = FastAPI(title="Anti-Slop MCP Server")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request models
class ContentRequest(BaseModel):
    content: str

class ImproveContentRequest(BaseModel):
    content: str
    preserve_meaning: bool = True
    target_tone: str = "professional"

class DetectRepetitionRequest(BaseModel):
    content: str
    min_length: int = 3

class DetectRunOnSentencesRequest(BaseModel):
    content: str
    max_words: int = 30

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "anti-slop-mcp"}

# Analyze content for slop
@app.post("/analyze_content_for_slop")
async def analyze_content_for_slop(request: ContentRequest):
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
                    "content": f"Analyze this content:\n\n{request.content}"
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        analysis = json.loads(completion.choices[0].message.content)
        
        return {
            "content": request.content,
            "analysis": {
                "score": analysis.get("score", 0),
                "issues": analysis.get("issues", []),
                "suggestions": analysis.get("suggestions", [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze content: {str(e)}")

# Remove em dashes
@app.post("/remove_em_dashes")
async def remove_em_dashes(request: ContentRequest):
    cleaned = request.content.replace("—", "-")
    count = request.content.count("—")
    
    return {
        "original_content": request.content,
        "cleaned_content": cleaned,
        "removals": {
            "em_dashes_removed": count
        }
    }

# Remove emojis
@app.post("/remove_emojis")
async def remove_emojis(request: ContentRequest):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F1E0-\U0001F1FF"  # flags
        "]+",
        flags=re.UNICODE
    )
    
    emojis = emoji_pattern.findall(request.content)
    cleaned = emoji_pattern.sub('', request.content)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return {
        "original_content": request.content,
        "cleaned_content": cleaned,
        "removals": {
            "emojis_removed": len(emojis),
            "emojis_found": emojis
        }
    }

# Detect AI phrases
@app.post("/detect_ai_phrases")
async def detect_ai_phrases(request: ContentRequest):
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
        matches = pattern.findall(request.content)
        if matches:
            found.append({
                "phrase": phrase,
                "count": len(matches),
                "instances": matches
            })
    
    return {
        "content": request.content,
        "ai_phrases_detected": len(found),
        "total_instances": sum(item["count"] for item in found),
        "phrases": found,
        "slop_score": min(10, len(found) * 2)
    }

# Remove filler words
@app.post("/remove_filler_words")
async def remove_filler_words(request: ContentRequest):
    filler_words = ['actually', 'basically', 'literally', 'just', 'very', 'really', 'quite', 'rather', 'somewhat', 'perhaps', 'maybe']
    found = {}
    cleaned = request.content
    
    for word in filler_words:
        pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
        matches = pattern.findall(request.content)
        if matches:
            found[word] = len(matches)
            cleaned = pattern.sub('', cleaned)
    
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned).strip()
    
    return {
        "original_content": request.content,
        "cleaned_content": cleaned,
        "filler_words_removed": sum(found.values()),
        "breakdown": found
    }

# Detect cliches
@app.post("/detect_cliches")
async def detect_cliches(request: ContentRequest):
    cliches = [
        'at the end of the day',
        'think outside the box',
        'game changer',
        'low-hanging fruit',
        'move the needle',
        'paradigm shift',
        'synergy',
        'win-win',
        'touch base',
        'circle back',
        'take it to the next level',
        'best of breed',
        'industry leading',
        'world class',
        'bleeding edge',
        'mission critical',
        'seamless integration',
        'turnkey solution',
        'value add',
        'best in class',
        'drill down',
        'bandwidth',
        'actionable insights',
        'core competency'
    ]
    
    found = []
    for cliche in cliches:
        pattern = re.compile(r'\b' + re.escape(cliche) + r'\b', re.IGNORECASE)
        matches = pattern.findall(request.content)
        if matches:
            found.append({"cliche": cliche, "count": len(matches)})
    
    return {
        "content": request.content,
        "cliches_detected": len(found),
        "total_instances": sum(item["count"] for item in found),
        "cliches": found
    }

# Remove hedging
@app.post("/remove_hedging")
async def remove_hedging(request: ContentRequest):
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
    cleaned = request.content
    
    for phrase in hedge_phrases:
        pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
        matches = pattern.findall(request.content)
        if matches:
            found[phrase] = len(matches)
            cleaned = pattern.sub('', cleaned)
    
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned).strip()
    
    return {
        "original_content": request.content,
        "cleaned_content": cleaned,
        "hedging_removed": sum(found.values()),
        "breakdown": found
    }

# Detect passive voice
@app.post("/detect_passive_voice")
async def detect_passive_voice(request: ContentRequest):
    passive_patterns = [
        re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE),
        re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+en\b', re.IGNORECASE)
    ]
    
    matches = []
    for pattern in passive_patterns:
        found = pattern.findall(request.content)
        matches.extend(found)
    
    sentences = [s.strip() for s in re.split(r'[.!?]+', request.content) if s.strip()]
    passive_sentences = [s for s in sentences if any(p.search(s) for p in passive_patterns)]
    
    return {
        "content": request.content,
        "passive_voice_detected": len(matches),
        "passive_phrases": list(set(matches)),
        "passive_sentence_count": len(passive_sentences),
        "total_sentences": len(sentences),
        "passive_percentage": round((len(passive_sentences) / len(sentences)) * 100) if sentences else 0
    }

# Normalize whitespace
@app.post("/normalize_whitespace")
async def normalize_whitespace(request: ContentRequest):
    normalized = request.content
    normalized = normalized.replace('\t', ' ')
    normalized = re.sub(r' +', ' ', normalized)
    normalized = re.sub(r'\n\n+', '\n\n', normalized)
    normalized = normalized.replace('\r\n', '\n')
    normalized = normalized.strip()
    
    return {
        "original_content": request.content,
        "normalized_content": normalized,
        "changes": {
            "original_length": len(request.content),
            "normalized_length": len(normalized),
            "characters_removed": len(request.content) - len(normalized)
        }
    }

# Calculate readability
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

@app.post("/calculate_readability")
async def calculate_readability(request: ContentRequest):
    sentences = len([s for s in re.split(r'[.!?]+', request.content) if s.strip()])
    words_list = [w for w in request.content.split() if w.strip()]
    words = len(words_list)
    syllables = sum(count_syllables(word) for word in words_list)
    
    avg_sentence_length = words / sentences if sentences > 0 else 0
    avg_syllables_per_word = syllables / words if words > 0 else 0
    
    flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    grade_level = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    
    return {
        "content": request.content,
        "stats": {
            "sentences": sentences,
            "words": words,
            "syllables": syllables,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_syllables_per_word": round(avg_syllables_per_word, 1)
        },
        "readability": {
            "flesch_reading_ease": max(0, min(100, round(flesch_score))),
            "grade_level": max(0, round(grade_level, 1)),
            "difficulty": get_reading_difficulty(flesch_score)
        }
    }

# Detect repetition
@app.post("/detect_repetition")
async def detect_repetition(request: DetectRepetitionRequest):
    words = [w.lower() for w in request.content.split() if w.strip()]
    phrases = {}
    
    for length in range(request.min_length, 6):
        for i in range(len(words) - length + 1):
            phrase = ' '.join(words[i:i + length])
            phrases[phrase] = phrases.get(phrase, 0) + 1
    
    repeated = [
        {"phrase": phrase, "count": count}
        for phrase, count in phrases.items()
        if count > 1
    ]
    repeated.sort(key=lambda x: x["count"], reverse=True)
    repeated = repeated[:20]
    
    return {
        "content": request.content,
        "repeated_phrases": len(repeated),
        "phrases": repeated,
        "repetition_score": min(10, len(repeated) // 2)
    }

# Detect run-on sentences
@app.post("/detect_run_on_sentences")
async def detect_run_on_sentences(request: DetectRunOnSentencesRequest):
    sentences = [s.strip() for s in re.split(r'[.!?]+', request.content) if s.strip()]
    
    run_on_sentences = [
        {
            "sentence": sentence,
            "word_count": len(sentence.split())
        }
        for sentence in sentences
        if len(sentence.split()) > request.max_words
    ]
    
    return {
        "content": request.content,
        "total_sentences": len(sentences),
        "run_on_sentences": len(run_on_sentences),
        "sentences": run_on_sentences,
        "percentage": round((len(run_on_sentences) / len(sentences)) * 100) if sentences else 0
    }

# Remove redundancies
@app.post("/remove_redundancies")
async def remove_redundancies(request: ContentRequest):
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
    
    cleaned = request.content
    found = []
    
    for item in redundancies:
        pattern = re.compile(r'\b' + re.escape(item['phrase']) + r'\b', re.IGNORECASE)
        matches = pattern.findall(request.content)
        if matches:
            found.append({
                "phrase": item['phrase'],
                "replacement": item['replacement'],
                "count": len(matches)
            })
            cleaned = pattern.sub(item['replacement'], cleaned)
    
    return {
        "original_content": request.content,
        "cleaned_content": cleaned,
        "redundancies_removed": len(found),
        "changes": found
    }

# Improve content from slop
@app.post("/improve_content_from_slop")
async def improve_content_from_slop(request: ImproveContentRequest):
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a content improvement specialist. Rewrite the given text to remove "slop" while {'preserving the original meaning' if request.preserve_meaning else 'focusing on clarity'}. 

Remove:
- Unnecessary qualifiers and hedging language
- Generic phrases and clichés
- Repetitive statements
- Excessive verbosity
- Overused AI phrases like "delve into", "it's worth noting", "in today's world"

Make the content:
- Concise and direct
- Specific and concrete
- {request.target_tone} in tone
- More impactful

Return a JSON response with:
- improved_content (the rewritten text)
- changes_made (array describing what was improved)
- original_word_count
- new_word_count"""
                },
                {
                    "role": "user",
                    "content": f"Improve this content:\n\n{request.content}"
                }
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(completion.choices[0].message.content)
        
        return {
            "original_content": request.content,
            "improved_content": result.get("improved_content", request.content),
            "changes_made": result.get("changes_made", []),
            "stats": {
                "original_word_count": result.get("original_word_count", len(request.content.split())),
                "new_word_count": result.get("new_word_count", len(result.get("improved_content", request.content).split()))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to improve content: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
