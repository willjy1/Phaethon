"""Content scoring engine."""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..core.schemas import (
    ContentItem,
    UserProfile,
    ScoringResult,
    InterventionAction,
    ContentFeatures,
)
from .content_features import ContentFeatureExtractor

logger = logging.getLogger(__name__)


class ContentScorer:
    """Scores content against user values."""
    
    def __init__(self):
        """Initialize content scorer."""
        self.feature_extractor = ContentFeatureExtractor()
    
    def score_content(self, content: ContentItem, user_profile: UserProfile) -> ScoringResult:
        """Score content against user's values.
        
        Args:
            content: ContentItem to score.
            user_profile: User's profile with values.
        
        Returns:
            ScoringResult with detailed scoring information.
        """
        # Extract features if not already done
        if content.extracted_features is None:
            content.extracted_features = self.feature_extractor.extract_features(content)
        
        features = content.extracted_features
        values = user_profile.values.values
        
        # Calculate alignment scores for each value dimension
        scores_by_value = self._calculate_value_alignment(content, features, values)
        
        # Aggregate to overall alignment score
        alignment_score = self._aggregate_alignment_score(scores_by_value)
        
        # Estimate productivity and wellbeing impact
        productivity_impact = self._estimate_productivity_impact(content, features, scores_by_value)
        wellbeing_impact = self._estimate_wellbeing_impact(content, features, scores_by_value)
        
        # Calculate confidence based on feature completeness
        confidence = self._calculate_confidence(content, features)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(alignment_score, productivity_impact, wellbeing_impact)
        
        # Recommend action
        recommended_action = self._recommend_action(alignment_score, wellbeing_impact)
        
        return ScoringResult(
            content_id=content.content_id,
            user_id=user_profile.user_id,
            alignment_score=alignment_score,
            productivity_impact=productivity_impact,
            wellbeing_impact=wellbeing_impact,
            confidence=confidence,
            scores_by_value=scores_by_value,
            reasoning=reasoning,
            recommended_action=recommended_action,
            timestamp=datetime.utcnow(),
        )
    
    def _calculate_value_alignment(self, content: ContentItem, features: ContentFeatures,
                                  values: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate alignment score for each value dimension.
        
        Args:
            content: Content being scored.
            features: Extracted features.
            values: User's values hierarchy.
        
        Returns:
            Dict mapping value names to alignment scores (0-1).
        """
        scores = {}
        
        # Learning values
        if "learning" in values.get("productivity", {}):
            learning_value = values["productivity"]["learning"]
            # Articles and educational content align with learning
            is_learning_content = (
                content.content_type.value == "article" or
                features.tone == "educational" or
                any(topic in ["science", "technology", "productivity"] for topic in features.main_topics)
            )
            learning_alignment = 0.8 if is_learning_content else 0.3
            scores["learning"] = learning_value * learning_alignment
        
        # Focus values
        if "focus" in values.get("productivity", {}):
            focus_value = values["productivity"]["focus"]
            # Long-form content with low novelty supports focus
            is_distraction_domain = content.domain in ContentFeatureExtractor.DISTRACTION_DOMAINS
            is_clickbait = features.is_clickbait
            focus_alignment = 0.2 if (is_distraction_domain or is_clickbait) else 0.8
            scores["focus"] = focus_value * focus_alignment
        
        # Sleep/wellbeing values
        if "sleep_quality" in values.get("wellbeing", {}):
            sleep_value = values["wellbeing"]["sleep_quality"]
            # Stressful/negative content affects sleep
            is_stressful = features.emotional_valence < -0.3 or any(
                topic in ["crisis", "disease", "attack"] for topic in features.main_topics
            )
            sleep_alignment = 0.2 if is_stressful else 0.7
            scores["sleep_quality"] = sleep_value * sleep_alignment
        
        # Output quality values
        if "output_quality" in values.get("productivity", {}):
            output_value = values["productivity"]["output_quality"]
            # Referential, source-rich content supports output quality
            is_high_quality_source = content.domain in ContentFeatureExtractor.LEARNING_DOMAINS
            output_alignment = 0.9 if is_high_quality_source else 0.4
            scores["output_quality"] = output_value * output_alignment
        
        return scores
    
    def _aggregate_alignment_score(self, scores_by_value: Dict[str, float]) -> float:
        """Aggregate individual value alignment scores.
        
        Args:
            scores_by_value: Individual alignment scores.
        
        Returns:
            Overall alignment score (0-1).
        """
        if not scores_by_value:
            return 0.5  # Neutral if no values
        
        avg_score = sum(scores_by_value.values()) / len(scores_by_value)
        return max(0.0, min(1.0, avg_score))
    
    def _estimate_productivity_impact(self, content: ContentItem, features: ContentFeatures,
                                     scores_by_value: Dict[str, float]) -> float:
        """Estimate impact on productivity (-1 to +1).
        
        Args:
            content: Content being scored.
            features: Extracted features.
            scores_by_value: Value alignment scores.
        
        Returns:
            Productivity impact score (-1 to +1).
        """
        # Content from learning domains has positive impact
        is_learning_domain = content.domain in ContentFeatureExtractor.LEARNING_DOMAINS
        learning_impact = 0.6 if is_learning_domain else 0.0
        
        # Distraction domains have negative impact
        is_distraction_domain = content.domain in ContentFeatureExtractor.DISTRACTION_DOMAINS
        distraction_impact = -0.5 if is_distraction_domain else 0.0
        
        # Clickbait/promotional has negative impact
        clickbait_impact = -0.3 if features.is_clickbait else 0.0
        promo_impact = -0.2 if features.is_promotional else 0.0
        
        # Sum impacts, clamped to [-1, 1]
        total_impact = learning_impact + distraction_impact + clickbait_impact + promo_impact
        return max(-1.0, min(1.0, total_impact))
    
    def _estimate_wellbeing_impact(self, content: ContentItem, features: ContentFeatures,
                                  scores_by_value: Dict[str, float]) -> float:
        """Estimate impact on wellbeing (-1 to +1).
        
        Args:
            content: Content being scored.
            features: Extracted features.
            scores_by_value: Value alignment scores.
        
        Returns:
            Wellbeing impact score (-1 to +1).
        """
        # Negative valence content has negative wellbeing impact
        valence = features.emotional_valence or 0.0
        valence_impact = valence * 0.5  # Moderate effect
        
        # Stressful content (news, crisis) affects wellbeing
        is_stressful = features.tone == "sensational" and valence < 0
        stress_impact = -0.3 if is_stressful else 0.0
        
        # Social media has slight negative impact
        is_social = content.domain in ["twitter.com", "facebook.com", "instagram.com"]
        social_impact = -0.1 if is_social else 0.0
        
        total_impact = valence_impact + stress_impact + social_impact
        return max(-1.0, min(1.0, total_impact))
    
    def _calculate_confidence(self, content: ContentItem, features: ContentFeatures) -> float:
        """Calculate confidence in scoring.
        
        Args:
            content: ContentItem.
            features: Extracted features.
        
        Returns:
            Confidence score (0-1).
        """
        confidence = 0.5
        
        # More complete metadata = higher confidence
        if content.metadata.author:
            confidence += 0.1
        if content.metadata.timestamp:
            confidence += 0.1
        if features.main_topics:
            confidence += 0.1
        if features.tone and features.tone != "neutral":
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, alignment_score: float, productivity_impact: float,
                          wellbeing_impact: float) -> str:
        """Generate human-readable reasoning for score.
        
        Args:
            alignment_score: Overall alignment score.
            productivity_impact: Estimated productivity effect.
            wellbeing_impact: Estimated wellbeing effect.
        
        Returns:
            Reasoning text.
        """
        parts = []
        
        if alignment_score > 0.7:
            parts.append("High alignment with your stated values")
        elif alignment_score > 0.4:
            parts.append("Moderate alignment with your values")
        else:
            parts.append("Low alignment with your stated values")
        
        if productivity_impact > 0.3:
            parts.append(f"likely increases productivity ({productivity_impact:+.0%})")
        elif productivity_impact < -0.3:
            parts.append(f"likely decreases productivity ({productivity_impact:+.0%})")
        
        if wellbeing_impact < -0.2:
            parts.append(f"may negatively affect wellbeing")
        
        return "; ".join(parts)
    
    def _recommend_action(self, alignment_score: float, wellbeing_impact: float) -> InterventionAction:
        """Recommend intervention action based on score.
        
        Args:
            alignment_score: Overall alignment score.
            wellbeing_impact: Estimated wellbeing effect.
        
        Returns:
            Recommended InterventionAction.
        """
        if alignment_score > 0.8 and wellbeing_impact > -0.2:
            return InterventionAction.ALLOW_PRIORITIZE
        elif alignment_score > 0.5:
            return InterventionAction.ALLOW
        elif alignment_score > 0.3:
            if wellbeing_impact < -0.3:
                return InterventionAction.ALLOW_WARNING
            return InterventionAction.ALLOW_MUTE
        else:
            return InterventionAction.BLOCK
