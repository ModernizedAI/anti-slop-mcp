"""Anti-slop package for detecting and cleaning low-quality AI-generated content."""
from .base import BaseTool, ToolResult
from .registry import ToolRegistry
from .enums import ToolName
from .analyzers import (
    AIPhrasesAnalyzer,
    ClicheAnalyzer,
    PassiveVoiceAnalyzer,
    ReadabilityAnalyzer,
    RepetitionAnalyzer,
    RunOnSentenceAnalyzer,
)
from .cleaners import (
    FillerWordsCleaner,
    HedgingCleaner,
    RedundancyCleaner,
    EmojiCleaner,
    WhitespaceCleaner,
)
from .ai_tools import ContentAnalyzer, ContentImprover

__version__ = "1.0.0"

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "ToolName",
    "AIPhrasesAnalyzer",
    "ClicheAnalyzer",
    "PassiveVoiceAnalyzer",
    "ReadabilityAnalyzer",
    "RepetitionAnalyzer",
    "RunOnSentenceAnalyzer",
    "FillerWordsCleaner",
    "HedgingCleaner",
    "RedundancyCleaner",
    "EmojiCleaner",
    "WhitespaceCleaner",
    "ContentAnalyzer",
    "ContentImprover",
]
