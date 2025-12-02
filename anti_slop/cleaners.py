"""Cleaning tools for removing slop patterns."""
import re
from typing import Dict, List
from .base import BaseTool, ToolResult
from .enums import ToolName


class FillerWordsCleaner(BaseTool):
    """Remove filler words from text."""
    
    FILLER_WORDS = [
        'actually', 'basically', 'literally', 'just', 'very', 
        'really', 'quite', 'rather', 'somewhat', 'perhaps', 'maybe'
    ]
    
    @property
    def name(self) -> str:
        return ToolName.REMOVE_FILLER_WORDS.value
    
    @property
    def description(self) -> str:
        return "Remove filler words like 'actually', 'basically', 'literally', 'just', 'very', 'really', etc."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        found = {}
        cleaned = content
        
        for word in self.FILLER_WORDS:
            pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found[word] = len(matches)
                cleaned = pattern.sub('', cleaned)
        
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned).strip()
        
        return ToolResult(
            success=True,
            data={
                "original_content": content,
                "cleaned_content": cleaned,
                "filler_words_removed": sum(found.values()),
                "breakdown": found,
            }
        )


class HedgingCleaner(BaseTool):
    """Remove hedging language from text."""
    
    HEDGE_PHRASES = [
        'it seems', 'it appears', 'it might be', 'it could be',
        'perhaps', 'maybe', 'possibly', 'probably',
        'might', 'could', 'may', 'would seem',
        'in some ways', 'to some extent', 'sort of', 'kind of',
        'I think', 'I believe', 'I feel',
        'somewhat', 'fairly', 'relatively',
        'could potentially', 'might possibly'
    ]
    
    @property
    def name(self) -> str:
        return ToolName.REMOVE_HEDGING.value
    
    @property
    def description(self) -> str:
        return "Remove hedging language like 'perhaps', 'maybe', 'might', 'it seems', etc. to make text more direct."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        found = {}
        cleaned = content
        
        for phrase in self.HEDGE_PHRASES:
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found[phrase] = len(matches)
                cleaned = pattern.sub('', cleaned)
        
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned).strip()
        
        return ToolResult(
            success=True,
            data={
                "original_content": content,
                "cleaned_content": cleaned,
                "hedging_removed": sum(found.values()),
                "breakdown": found,
            }
        )


class RedundancyCleaner(BaseTool):
    """Remove redundant phrases from text."""
    
    REDUNDANCIES = [
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
    
    @property
    def name(self) -> str:
        return ToolName.REMOVE_REDUNDANCIES.value
    
    @property
    def description(self) -> str:
        return "Remove redundant phrases like 'past history', 'future plans', 'absolutely essential', etc."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        cleaned = content
        found = []
        
        for item in self.REDUNDANCIES:
            pattern = re.compile(r'\b' + re.escape(item['phrase']) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found.append({
                    "phrase": item['phrase'],
                    "replacement": item['replacement'],
                    "count": len(matches)
                })
                cleaned = pattern.sub(item['replacement'], cleaned)
        
        return ToolResult(
            success=True,
            data={
                "original_content": content,
                "cleaned_content": cleaned,
                "redundancies_removed": len(found),
                "changes": found,
            }
        )


class EmojiCleaner(BaseTool):
    """Remove emojis from text."""
    
    EMOJI_PATTERN = re.compile(
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
    
    @property
    def name(self) -> str:
        return ToolName.REMOVE_EMOJIS.value
    
    @property
    def description(self) -> str:
        return "Remove all emojis from text."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        emojis = self.EMOJI_PATTERN.findall(content)
        cleaned = self.EMOJI_PATTERN.sub('', content)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return ToolResult(
            success=True,
            data={
                "original_content": content,
                "cleaned_content": cleaned,
                "emojis_removed": len(emojis),
                "emojis_found": emojis,
            }
        )


class WhitespaceCleaner(BaseTool):
    """Normalize whitespace in text."""
    
    @property
    def name(self) -> str:
        return ToolName.NORMALIZE_WHITESPACE.value
    
    @property
    def description(self) -> str:
        return "Normalize whitespace, removing extra spaces, tabs, and blank lines."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        normalized = content
        normalized = normalized.replace('\t', ' ')
        normalized = re.sub(r' +', ' ', normalized)
        normalized = re.sub(r'\n\n+', '\n\n', normalized)
        normalized = normalized.replace('\r\n', '\n')
        normalized = normalized.strip()
        
        chars_removed = len(content) - len(normalized)
        
        return ToolResult(
            success=True,
            data={
                "original_content": content,
                "normalized_content": normalized,
                "characters_removed": chars_removed,
            }
        )
