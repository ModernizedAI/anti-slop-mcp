"""Enums and constants for anti-slop tools."""
from enum import Enum


class ToolName(str, Enum):
    """Enum for all available tool names."""
    
    # Analyzers
    DETECT_AI_PHRASES = "detect_ai_phrases"
    DETECT_CLICHES = "detect_cliches"
    DETECT_PASSIVE_VOICE = "detect_passive_voice"
    CALCULATE_READABILITY = "calculate_readability"
    DETECT_REPETITION = "detect_repetition"
    DETECT_RUN_ON_SENTENCES = "detect_run_on_sentences"
    
    # Cleaners
    REMOVE_FILLER_WORDS = "remove_filler_words"
    REMOVE_HEDGING = "remove_hedging"
    REMOVE_REDUNDANCIES = "remove_redundancies"
    REMOVE_EMOJIS = "remove_emojis"
    NORMALIZE_WHITESPACE = "normalize_whitespace"
    
    # AI Tools
    ANALYZE_CONTENT_FOR_SLOP = "analyze_content_for_slop"
    IMPROVE_CONTENT_FROM_SLOP = "improve_content_from_slop"
    
    @classmethod
    def list_all(cls) -> list[str]:
        """Get list of all tool names."""
        return [tool.value for tool in cls]
    
    @classmethod
    def is_valid(cls, name: str) -> bool:
        """Check if a tool name is valid."""
        return name in cls._value2member_map_
