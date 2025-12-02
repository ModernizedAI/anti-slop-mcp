"""Formatters for converting tool results to different output formats."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from anti_slop.base import ToolResult


class BaseFormatter(ABC):
    """Base formatter for tool results."""
    
    @abstractmethod
    def format(self, result: ToolResult) -> Any:
        """Format a tool result."""
        pass


class TextFormatter(BaseFormatter):
    """Format tool results as human-readable text."""
    
    def format(self, result: ToolResult) -> str:
        """Format a tool result as text."""
        if not result.success:
            return f"Error: {result.error}"
        
        data = result.data
        response_parts = []
        
        # Determine formatter method based on data structure
        if "cleaned_content" in data:
            response_parts = self._format_cleaned_content(data)
        elif "normalized_content" in data:
            response_parts = self._format_normalized_content(data)
        elif "phrases_detected" in data:
            response_parts = self._format_ai_phrases(data)
        elif "cliches_detected" in data:
            response_parts = self._format_cliches(data)
        elif "passive_percentage" in data:
            response_parts = self._format_passive_voice(data)
        elif "readability" in data:
            response_parts = self._format_readability(data)
        elif "repeated_phrases" in data:
            response_parts = self._format_repetition(data)
        elif "run_on_sentences" in data:
            response_parts = self._format_run_on_sentences(data)
        elif "score" in data:
            response_parts = self._format_analysis(data)
        elif "improved_content" in data:
            response_parts = self._format_improved_content(data)
        else:
            response_parts = [str(data)]
        
        return "\n".join(response_parts)
    
    def _format_cleaned_content(self, data: Dict[str, Any]) -> List[str]:
        """Format cleaned content results."""
        parts = [f"Cleaned Content:\n{data['cleaned_content']}\n"]
        
        if "filler_words_removed" in data:
            parts.append(f"Removed {data['filler_words_removed']} filler words")
            if data.get("breakdown"):
                parts.append(":\n" + "\n".join(
                    f"- {word}: {count}" for word, count in data["breakdown"].items()
                ))
        elif "hedging_removed" in data:
            parts.append(f"Removed {data['hedging_removed']} hedging phrases")
            if data.get("breakdown"):
                parts.append(":\n" + "\n".join(
                    f"- '{phrase}': {count}" for phrase, count in data["breakdown"].items()
                ))
        elif "redundancies_removed" in data:
            parts.append(f"Removed {data['redundancies_removed']} redundancies")
            if data.get("changes"):
                parts.append(":\n" + "\n".join(
                    f"- '{c['phrase']}' → '{c['replacement']}' ({c['count']} times)" 
                    for c in data["changes"]
                ))
        elif "emojis_removed" in data:
            parts.append(f"Removed {data['emojis_removed']} emoji(s)")
        
        return parts
    
    def _format_normalized_content(self, data: Dict[str, Any]) -> List[str]:
        """Format normalized content results."""
        return [
            f"Normalized Content:\n{data['normalized_content']}\n",
            f"Removed {data['characters_removed']} extra whitespace character(s)"
        ]
    
    def _format_ai_phrases(self, data: Dict[str, Any]) -> List[str]:
        """Format AI phrases detection results."""
        parts = [
            f"AI Phrases Detected: {data['phrases_detected']}",
            f"Slop Score: {data['slop_score']}/10\n"
        ]
        
        if data['phrases']:
            parts.append("\n".join(
                f"'{p['phrase']}' - found {p['count']} time(s)" 
                for p in data['phrases']
            ))
        else:
            parts.append("No AI phrases detected. Content looks clean!")
        
        return parts
    
    def _format_cliches(self, data: Dict[str, Any]) -> List[str]:
        """Format cliché detection results."""
        parts = [f"Clichés Detected: {data['cliches_detected']}\n"]
        
        if data['cliches']:
            parts.append("\n".join(
                f"'{c['cliche']}' - {c['count']} time(s)" 
                for c in data['cliches']
            ))
        else:
            parts.append("No clichés detected!")
        
        return parts
    
    def _format_passive_voice(self, data: Dict[str, Any]) -> List[str]:
        """Format passive voice analysis results."""
        recommendation = (
            "Consider rewriting in active voice" 
            if data['passive_percentage'] > 20 
            else "Passive voice usage is acceptable"
        )
        
        return [
            "Passive Voice Analysis:",
            f"Total Sentences: {data['total_sentences']}",
            f"Passive Sentences: {data['passive_sentences']} ({data['passive_percentage']}%)",
            f"Passive Phrases Found: {data['passive_phrases_found']}\n",
            f"Recommendation: {recommendation}"
        ]
    
    def _format_readability(self, data: Dict[str, Any]) -> List[str]:
        """Format readability analysis results."""
        stats = data['stats']
        read = data['readability']
        
        return [
            "Readability Analysis:",
            f"Flesch Reading Ease: {read['flesch_reading_ease']}/100",
            f"Difficulty: {read['difficulty']}",
            f"Grade Level: {read['grade_level']}\n",
            "Statistics:",
            f"- Sentences: {stats['sentences']}",
            f"- Words: {stats['words']}",
            f"- Syllables: {stats['syllables']}",
            f"- Avg Sentence Length: {stats['avg_sentence_length']} words",
            f"- Avg Syllables per Word: {stats['avg_syllables_per_word']}"
        ]
    
    def _format_repetition(self, data: Dict[str, Any]) -> List[str]:
        """Format repetition detection results."""
        parts = [f"Repeated Phrases Found: {data['repeated_phrases']}\n"]
        
        if data['phrases']:
            parts.append("\n".join(
                f"'{p['phrase']}' - {p['count']} times" 
                for p in data['phrases']
            ))
        else:
            parts.append("No significant repetition detected.")
        
        return parts
    
    def _format_run_on_sentences(self, data: Dict[str, Any]) -> List[str]:
        """Format run-on sentence detection results."""
        parts = [
            "Run-on Sentence Analysis:",
            f"Total Sentences: {data['total_sentences']}",
            f"Run-on Sentences: {data['run_on_sentences']} ({data['percentage']}%)\n"
        ]
        
        if data['sentences']:
            parts.append("Run-on sentences found:")
            parts.append("\n".join(
                f"- {s['word_count']} words: {s['sentence']}" 
                for s in data['sentences'][:5]
            ))
        else:
            parts.append("No run-on sentences detected!")
        
        return parts
    
    def _format_analysis(self, data: Dict[str, Any]) -> List[str]:
        """Format content analysis results."""
        parts = [
            "Analysis Results:",
            f"Score: {data['score']}/10\n",
            "Issues Found:",
            "\n".join(f"- {issue}" for issue in data.get('issues', [])),
            "\nSuggestions:",
            "\n".join(f"- {suggestion}" for suggestion in data.get('suggestions', []))
        ]
        
        return parts
    
    def _format_improved_content(self, data: Dict[str, Any]) -> List[str]:
        """Format improved content results."""
        return [
            f"Improved Content:\n{data['improved_content']}\n",
            "Changes Made:",
            "\n".join(f"- {change}" for change in data.get('changes_made', [])),
            f"\nWord Count: {data['original_word_count']} → {data['new_word_count']}"
        ]


class JSONFormatter(BaseFormatter):
    """Format tool results as JSON."""
    
    def format(self, result: ToolResult) -> Dict[str, Any]:
        """Format a tool result as JSON-compatible dict."""
        if not result.success:
            return {
                "success": False,
                "error": result.error
            }
        
        return {
            "success": True,
            "data": result.data
        }
