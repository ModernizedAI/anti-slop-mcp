"""AI-powered analysis and improvement tools."""
import json
import os
from typing import Optional
from openai import OpenAI
from .base import BaseTool, ToolResult
from .enums import ToolName


class ContentAnalyzer(BaseTool):
    """Analyze content for slop using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    @property
    def name(self) -> str:
        return ToolName.ANALYZE_CONTENT_FOR_SLOP.value
    
    @property
    def description(self) -> str:
        return "Analyze text for low-quality AI-generated content. Returns a score (0-10) where higher means more slop, plus specific issues and suggestions."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        if not self.client:
            return ToolResult(
                success=False,
                data={},
                error="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )
        
        try:
            completion = self.client.chat.completions.create(
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
            
            analysis = json.loads(completion.choices[0].message.content)
            
            return ToolResult(
                success=True,
                data={
                    "score": analysis.get("score", 0),
                    "issues": analysis.get("issues", []),
                    "suggestions": analysis.get("suggestions", []),
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to analyze content: {str(e)}"
            )


class ContentImprover(BaseTool):
    """Improve content by removing slop using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    @property
    def name(self) -> str:
        return ToolName.IMPROVE_CONTENT_FROM_SLOP.value
    
    @property
    def description(self) -> str:
        return "Use AI to rewrite text, removing slop and improving clarity while preserving meaning."
    
    def execute(self, content: str, preserve_meaning: bool = True, target_tone: str = "professional", **kwargs) -> ToolResult:
        if not self.client:
            return ToolResult(
                success=False,
                data={},
                error="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )
        
        try:
            completion = self.client.chat.completions.create(
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
            
            result = json.loads(completion.choices[0].message.content)
            
            return ToolResult(
                success=True,
                data={
                    "improved_content": result.get("improved_content", content),
                    "changes_made": result.get("changes_made", []),
                    "original_word_count": result.get("original_word_count", len(content.split())),
                    "new_word_count": result.get("new_word_count", len(result.get("improved_content", content).split())),
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to improve content: {str(e)}"
            )
