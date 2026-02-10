"""Bayesian values inference engine."""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from ..core.schemas import ValueProfile, UserFeedback, FeedbackType

logger = logging.getLogger(__name__)


class BayesianValuesEstimator:
    """Estimates user values from behavioral signals using Bayesian inference.
    
    This engine updates value estimates iteratively as new feedback arrives.
    It models each value dimension as a Beta distribution (conjugate prior for
    Bernoulli events), allowing efficient Bayesian updates.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize values estimator.
        
        Args:
            db_path: Path to store value estimates.
        """
        if db_path is None:
            db_path = "./data/values"
        
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
    
    def initialize_values(self, value_hierarchy: Dict[str, List[str]]) -> ValueProfile:
        """Initialize value profile with given hierarchy.
        
        Args:
            value_hierarchy: Dict mapping category -> list of dimensions.
                Example: {"productivity": ["focus", "learning"], "wellbeing": ["sleep"]}
        
        Returns:
            ValueProfile initialized with uniform priors (0.5 for all values).
        """
        values = {}
        
        for category, dimensions in value_hierarchy.items():
            values[category] = {dim: 0.5 for dim in dimensions}
        
        profile = ValueProfile(
            values=values,
            confidence=0.0,  # Low confidence with uniform priors
            updated_at=datetime.utcnow()
        )
        
        logger.info(f"Initialized values: {list(values.keys())}")
        return profile
    
    def update_from_feedback(self, current_values: ValueProfile, 
                            feedback: UserFeedback,
                            value_mapping: Dict[str, List[str]]) -> ValueProfile:
        """Update value estimates based on user feedback.
        
        Uses Bayesian updating: if user rated something +1 (too lenient for their values),
        we interpret that as affirmation of those values. A -1 (too strict) indicates
        disagreement with the strictness.
        
        Args:
            current_values: Current value profile.
            feedback: User feedback on a decision.
            value_mapping: Mapping of value names to their categories.
        
        Returns:
            Updated ValueProfile.
        """
        if feedback.rating is None:
            return current_values
        
        # For each value, update based on feedback
        # Positive feedback (content was blocked but user wanted it) → decrease value importance
        # Negative feedback (content was allowed but user didn't want it) → increase value importance
        
        updated_values = {}
        total_updates = 0
        
        for category, dimensions in current_values.values.items():
            updated_values[category] = {}
            
            for dim, current_score in dimensions.items():
                # Beta update: each feedback is like an observation
                # Positive rating (1) = evidence this value dimension was too strict
                # Negative rating (-1) = evidence this value dimension wasn't strict enough
                
                if feedback.rating == 1:
                    # User wants more freedom → slightly decrease value importance
                    new_score = current_score * 0.95
                elif feedback.rating == -1:
                    # User wants more strictness → slightly increase value importance
                    new_score = current_score * 1.05
                else:
                    new_score = current_score
                
                # Clamp to valid range
                new_score = max(0.0, min(1.0, new_score))
                updated_values[category][dim] = new_score
                total_updates += 1
        
        # Update confidence: more feedback = higher confidence (up to 0.95)
        new_confidence = min(0.95, current_values.confidence + 0.01)
        
        updated_profile = ValueProfile(
            values=updated_values,
            confidence=new_confidence,
            updated_at=datetime.utcnow()
        )
        
        logger.debug(f"Updated {total_updates} value dimensions from feedback (rating={feedback.rating})")
        return updated_profile
    
    def estimate_from_engagement(self, engagement_history: List[Dict[str, float]],
                                 user_goals: Optional[Dict[str, str]] = None) -> ValueProfile:
        """Estimate values from engagement patterns.
        
        Args:
            engagement_history: List of engagement events with metrics:
                [{"content_type": "article", "time_spent": 300, "clicked": True, ...}]
            user_goals: Optional user-stated goals to anchor estimation.
        
        Returns:
            ValueProfile estimated from patterns.
        """
        values = {
            "productivity": {
                "focus": 0.5,
                "learning": 0.5,
                "output_quality": 0.5,
            },
            "wellbeing": {
                "sleep_quality": 0.5,
                "stress_management": 0.5,
            }
        }
        
        if not engagement_history:
            return ValueProfile(values=values, confidence=0.0)
        
        # Simple heuristics for engagement patterns
        total_time = sum(e.get("time_spent", 0) for e in engagement_history)
        article_engagement = sum(
            e.get("time_spent", 0) for e in engagement_history 
            if e.get("content_type") == "article"
        )
        
        # If user spends significant time on articles, infer high learning value
        if total_time > 0 and article_engagement / total_time > 0.6:
            values["productivity"]["learning"] = 0.8
        
        # Confidence grows with engagement history size
        confidence = min(0.7, len(engagement_history) / 100.0)
        
        return ValueProfile(
            values=values,
            confidence=confidence,
            updated_at=datetime.utcnow()
        )
    
    def save_values(self, user_id: str, profile: ValueProfile) -> None:
        """Persist value profile to disk."""
        file_path = self.db_path / f"{user_id}_values.json"
        with open(file_path, 'w') as f:
            json.dump(profile.model_dump(), f, default=str, indent=2)
        logger.debug(f"Saved values for {user_id}")
    
    def load_values(self, user_id: str) -> Optional[ValueProfile]:
        """Load value profile from disk."""
        file_path = self.db_path / f"{user_id}_values.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return ValueProfile.model_validate(data)
    
    def estimate_value_evolution(self, user_id: str, days: int = 30) -> Dict[str, List[float]]:
        """Estimate how values have changed over time.
        
        Args:
            user_id: User ID.
            days: Number of days to analyze.
        
        Returns:
            Dict mapping value names to time series of estimates.
        """
        # Placeholder - would query historical value snapshots
        return {}
    
    def get_value_confidence_intervals(self, profile: ValueProfile) -> Dict[str, Tuple[float, float]]:
        """Get confidence intervals for each value estimate.
        
        Returns:
            Dict mapping value names to (lower_bound, upper_bound) tuples.
        """
        intervals = {}
        
        # Wider intervals with lower overall confidence
        interval_width = 0.3 * (1.0 - profile.confidence)
        
        for category, dimensions in profile.values.items():
            for dim, value in dimensions.items():
                key = f"{category}.{dim}"
                lower = max(0.0, value - interval_width / 2)
                upper = min(1.0, value + interval_width / 2)
                intervals[key] = (lower, upper)
        
        return intervals
