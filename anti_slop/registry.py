"""Tool registry for managing all anti-slop tools."""
from typing import Dict, List, Optional
from .base import BaseTool, ToolResult
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


class ToolRegistry:
    """Registry for all anti-slop tools."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self._tools: Dict[str, BaseTool] = {}
        self._register_tools(openai_api_key)
    
    def _register_tools(self, openai_api_key: Optional[str]):
        """Register all available tools."""
        # Analyzers
        self.register(AIPhrasesAnalyzer())
        self.register(ClicheAnalyzer())
        self.register(PassiveVoiceAnalyzer())
        self.register(ReadabilityAnalyzer())
        self.register(RepetitionAnalyzer())
        self.register(RunOnSentenceAnalyzer())
        
        # Cleaners
        self.register(FillerWordsCleaner())
        self.register(HedgingCleaner())
        self.register(RedundancyCleaner())
        self.register(EmojiCleaner())
        self.register(WhitespaceCleaner())
        
        # AI-powered tools
        self.register(ContentAnalyzer(openai_api_key))
        self.register(ContentImprover(openai_api_key))
    
    def register(self, tool: BaseTool):
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[BaseTool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def execute_tool(self, name: str | ToolName, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool_name = name.value if isinstance(name, ToolName) else name
        
        if not ToolName.is_valid(tool_name):
            return ToolResult(
                success=False,
                data={},
                error=f"Unknown tool: {tool_name}. Valid tools: {', '.join(ToolName.list_all())}"
            )
        
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                data={},
                error=f"Tool '{tool_name}' not found in registry"
            )
        
        return tool.execute(**kwargs)
