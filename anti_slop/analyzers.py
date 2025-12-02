"""Analysis tools for detecting slop patterns."""
import re
from typing import Dict, Any, List
from .base import BaseTool, ToolResult
from .enums import ToolName


class AIPhrasesAnalyzer(BaseTool):
    """Detect common AI-generated phrases."""
    
    PHRASES = [
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
    
    @property
    def name(self) -> str:
        return ToolName.DETECT_AI_PHRASES.value
    
    @property
    def description(self) -> str:
        return "Detect common AI-generated phrases like 'delve into', 'it's worth noting', 'in today's world', etc."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        found = []
        for phrase in self.PHRASES:
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found.append({
                    "phrase": phrase,
                    "count": len(matches),
                })
        
        slop_score = min(10, len(found) * 2)
        
        return ToolResult(
            success=True,
            data={
                "phrases_detected": len(found),
                "slop_score": slop_score,
                "phrases": found,
            }
        )


class ClicheAnalyzer(BaseTool):
    """Detect business clichés and buzzwords."""
    
    CLICHES = [
        'at the end of the day', 'think outside the box', 'game changer',
        'low-hanging fruit', 'move the needle', 'paradigm shift',
        'synergy', 'win-win', 'touch base', 'circle back',
        'take it to the next level', 'best of breed', 'industry leading',
        'world class', 'bleeding edge', 'mission critical',
        'seamless integration', 'turnkey solution', 'value add',
        'best in class', 'drill down', 'bandwidth',
        'actionable insights', 'core competency'
    ]
    
    @property
    def name(self) -> str:
        return ToolName.DETECT_CLICHES.value
    
    @property
    def description(self) -> str:
        return "Detect business clichés and buzzwords like 'game changer', 'synergy', 'low-hanging fruit', etc."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        found = []
        for cliche in self.CLICHES:
            pattern = re.compile(r'\b' + re.escape(cliche) + r'\b', re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                found.append({
                    "cliche": cliche,
                    "count": len(matches),
                })
        
        return ToolResult(
            success=True,
            data={
                "cliches_detected": len(found),
                "total_instances": sum(c["count"] for c in found),
                "cliches": found,
            }
        )


class PassiveVoiceAnalyzer(BaseTool):
    """Detect passive voice usage in text."""
    
    PATTERNS = [
        re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE),
        re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+en\b', re.IGNORECASE)
    ]
    
    @property
    def name(self) -> str:
        return ToolName.DETECT_PASSIVE_VOICE.value
    
    @property
    def description(self) -> str:
        return "Detect passive voice usage in text and calculate percentage of passive sentences."
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        matches = []
        for pattern in self.PATTERNS:
            found = pattern.findall(content)
            matches.extend(found)
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        passive_sentences = [s for s in sentences if any(p.search(s) for p in self.PATTERNS)]
        
        percentage = round((len(passive_sentences) / len(sentences)) * 100) if sentences else 0
        
        return ToolResult(
            success=True,
            data={
                "total_sentences": len(sentences),
                "passive_sentences": len(passive_sentences),
                "passive_percentage": percentage,
                "passive_phrases_found": len(matches),
            }
        )


class ReadabilityAnalyzer(BaseTool):
    """Calculate readability metrics."""
    
    @property
    def name(self) -> str:
        return ToolName.CALCULATE_READABILITY.value
    
    @property
    def description(self) -> str:
        return "Calculate Flesch reading ease score, grade level, and other readability metrics."
    
    @staticmethod
    def count_syllables(word: str) -> int:
        word = re.sub(r'[^a-z]', '', word.lower())
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
        word = re.sub(r'^y', '', word)
        syllables = re.findall(r'[aeiouy]{1,2}', word)
        return len(syllables) if syllables else 1
    
    @staticmethod
    def get_difficulty(flesch_score: float) -> str:
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
    
    def execute(self, content: str, **kwargs) -> ToolResult:
        sentences = len([s for s in re.split(r'[.!?]+', content) if s.strip()])
        words_list = [w for w in content.split() if w.strip()]
        words = len(words_list)
        syllables = sum(self.count_syllables(word) for word in words_list)
        
        avg_sentence_length = words / sentences if sentences > 0 else 0
        avg_syllables_per_word = syllables / words if words > 0 else 0
        
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))
        grade_level = max(0, 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59)
        
        return ToolResult(
            success=True,
            data={
                "stats": {
                    "sentences": sentences,
                    "words": words,
                    "syllables": syllables,
                    "avg_sentence_length": round(avg_sentence_length, 1),
                    "avg_syllables_per_word": round(avg_syllables_per_word, 1),
                },
                "readability": {
                    "flesch_reading_ease": round(flesch_score),
                    "grade_level": round(grade_level, 1),
                    "difficulty": self.get_difficulty(flesch_score),
                }
            }
        )


class RepetitionAnalyzer(BaseTool):
    """Find repeated phrases in text."""
    
    @property
    def name(self) -> str:
        return ToolName.DETECT_REPETITION.value
    
    @property
    def description(self) -> str:
        return "Find repeated phrases in text (helps identify redundant content)."
    
    def execute(self, content: str, min_length: int = 3, **kwargs) -> ToolResult:
        words = [w.lower() for w in content.split() if w.strip()]
        phrases = {}
        
        for length in range(min_length, 6):
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
        
        repetition_score = min(10, len(repeated) // 2)
        
        return ToolResult(
            success=True,
            data={
                "repeated_phrases": len(repeated),
                "phrases": repeated,
                "repetition_score": repetition_score,
            }
        )


class RunOnSentenceAnalyzer(BaseTool):
    """Detect overly long run-on sentences."""
    
    @property
    def name(self) -> str:
        return ToolName.DETECT_RUN_ON_SENTENCES.value
    
    @property
    def description(self) -> str:
        return "Detect overly long run-on sentences that should be split."
    
    def execute(self, content: str, max_words: int = 30, **kwargs) -> ToolResult:
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        run_on_sentences = [
            {
                "sentence": sentence[:100] + "..." if len(sentence) > 100 else sentence,
                "word_count": len(sentence.split())
            }
            for sentence in sentences
            if len(sentence.split()) > max_words
        ]
        
        percentage = round((len(run_on_sentences) / len(sentences)) * 100) if sentences else 0
        
        return ToolResult(
            success=True,
            data={
                "total_sentences": len(sentences),
                "run_on_sentences": len(run_on_sentences),
                "percentage": percentage,
                "sentences": run_on_sentences,
            }
        )
