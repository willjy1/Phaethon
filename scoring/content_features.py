"""Content feature extraction and analysis."""

import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

from ..core.schemas import ContentItem, ContentFeatures

logger = logging.getLogger(__name__)


class ContentFeatureExtractor:
    """Extracts features from content for scoring."""
    
    # Known distraction/low-value domains
    DISTRACTION_DOMAINS = {
        "twitter.com", "x.com",
        "tiktok.com",
        "reddit.com",
        "youtube.com",
        "instagram.com",
        "facebook.com",
        "twitch.tv",
    }
    
    # Known high-value domains
    LEARNING_DOMAINS = {
        "arxiv.org",
        "medium.com",
        "substack.com",
        "coursera.org",
        "edx.org",
        "github.com",
        "stackoverflow.com",
    }
    
    def __init__(self):
        """Initialize feature extractor."""
        pass
    
    def extract_features(self, content: ContentItem) -> ContentFeatures:
        """Extract features from content item.
        
        Args:
            content: ContentItem to analyze.
        
        Returns:
            ContentFeatures with extracted information.
        """
        features = ContentFeatures(
            title=content.title,
            summary=content.metadata.author or ""
        )
        
        # Extract topics from title/metadata
        features.main_topics = self._extract_topics(content.title)
        if content.metadata.topics:
            features.main_topics.extend(content.metadata.topics)
        features.main_topics = list(set(features.main_topics))  # Deduplicate
        
        # Analyze tone
        features.tone = self._analyze_tone(content.title)
        
        # Estimate emotional valence
        features.emotional_valence = self._estimate_valence(content.title)
        
        # Check for promotional/clickbait
        features.is_promotional = self._is_promotional(content.title)
        features.is_clickbait = self._is_clickbait(content.title)
        
        # Domain reputation
        features.domain_reputation = self._get_domain_reputation(content.domain)
        
        return features
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text using keyword detection."""
        if not text:
            return []
        
        text_lower = text.lower()
        topics = []
        
        # Common topic keywords
        topic_keywords = {
            "technology": ["ai", "ml", "python", "javascript", "code", "tech", "app", "software"],
            "business": ["startup", "business", "market", "sales", "ceo", "founder"],
            "health": ["health", "medical", "nutrition", "exercise", "wellness"],
            "science": ["research", "study", "experiment", "science", "physics"],
            "productivity": ["productivity", "efficiency", "focus", "habit", "time"],
            "finance": ["money", "stocks", "crypto", "investing", "financial"],
            "entertainment": ["movie", "music", "game", "comedy", "funny"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _analyze_tone(self, text: str) -> str:
        """Analyze tone of content."""
        if not text:
            return "neutral"
        
        text_lower = text.lower()
        
        # Check for emotional/sensational tone
        sensational_words = ["shocking", "incredible", "unbelievable", "amazing", "worst", "best"]
        if any(word in text_lower for word in sensational_words):
            return "sensational"
        
        # Check for educational tone
        educational_words = ["guide", "tutorial", "how to", "learn", "course", "explained"]
        if any(word in text_lower for word in educational_words):
            return "educational"
        
        # Check for news tone
        news_words = ["breaking", "news", "announced", "released", "report"]
        if any(word in text_lower for word in news_words):
            return "news"
        
        return "neutral"
    
    def _estimate_valence(self, text: str) -> float:
        """Estimate emotional valence (-1 to +1) of content.
        
        Negative valence often indicates distressing/stressful content.
        Positive valence might indicate feel-good but potentially distracting content.
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Negative words
        negative_words = [
            "crisis", "death", "destroyed", "failed", "worst", "tragic",
            "disaster", "attack", "lawsuit", "fraud", "scandal"
        ]
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        # Positive words
        positive_words = [
            "amazing", "incredible", "success", "breakthrough", "love",
            "happy", "joy", "beautiful", "wonderful"
        ]
        positive_score = sum(1 for word in positive_words if word in text_lower)
        
        total = negative_score + positive_score
        if total == 0:
            return 0.0
        
        valence = (positive_score - negative_score) / total
        return max(-1.0, min(1.0, valence))
    
    def _is_promotional(self, text: str) -> bool:
        """Detect if content is promotional."""
        if not text:
            return False
        
        text_lower = text.lower()
        promo_phrases = [
            "click here", "sign up", "limited offer", "buy now",
            "sponsored", "advertisement", "get yours", "exclusive offer"
        ]
        
        return any(phrase in text_lower for phrase in promo_phrases)
    
    def _is_clickbait(self, text: str) -> bool:
        """Detect if content is clickbait."""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Clickbait indicators
        clickbait_patterns = [
            r"doctors hate.*",
            r"you won't believe.*",
            r"this one weird trick.*",
            r"number \d+ will shock you.*",
            r"what happened next.*",
        ]
        
        for pattern in clickbait_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Excessive punctuation
        if text.count("!") > 3 or text.count("?") > 2:
            return True
        
        return False
    
    def _get_domain_reputation(self, domain: str) -> float:
        """Get reputation score for domain (0-1)."""
        if domain in self.LEARNING_DOMAINS:
            return 0.95
        
        if domain in self.DISTRACTION_DOMAINS:
            return 0.3
        
        # Default to neutral
        return 0.5
    
    def get_feature_summary(self, features: ContentFeatures) -> str:
        """Get human-readable summary of extracted features."""
        summary_parts = []
        
        if features.main_topics:
            summary_parts.append(f"Topics: {', '.join(features.main_topics)}")
        
        if features.tone and features.tone != "neutral":
            summary_parts.append(f"Tone: {features.tone}")
        
        if features.is_clickbait:
            summary_parts.append("⚠ Potential clickbait")
        
        if features.is_promotional:
            summary_parts.append("📢 Promotional content")
        
        return " | ".join(summary_parts) if summary_parts else "Generic content"
