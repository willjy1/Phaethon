"""Feedback processing and integration."""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..core.schemas import UserFeedback, FeedbackType, ValueProfile

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """Processes user feedback to improve value estimates and decision accuracy."""
    
    def __init__(self):
        """Initialize feedback processor."""
        self.feedback_buffer = []
        self.feedback_quality_scores = {}
    
    def process_explicit_feedback(self, feedback: UserFeedback) -> Tuple[str, float]:
        """Process explicit user rating feedback.
        
        Args:
            feedback: User feedback object.
        
        Returns:
            Tuple of (feedback_signal, confidence).
            Signal: "agree" (user agrees with decision), "disagree", "neutral".
            Confidence: 0-1 score for feedback reliability.
        """
        if feedback.rating is None:
            return "neutral", 0.0
        
        # Rating interpretation:
        # +1 = decision was too strict (user wanted to see this)
        # 0 = decision was neutral
        # -1 = decision was too lenient (user didn't want this)
        
        if feedback.rating == 1:
            return "dis_block_agree", 0.9  # User agrees we were too strict
        elif feedback.rating == -1:
            return "disagree_allow", 0.9   # User agrees we were too lenient
        else:
            return "neutral", 0.5
    
    def process_implicit_feedback(self, action: Optional[str], 
                                 time_spent: Optional[float]) -> Tuple[str, float]:
        """Process implicit feedback from user behavior.
        
        Args:
            action: Action taken ("viewed", "dismissed", "spent_time", etc).
            time_spent: Time user spent with content (seconds).
        
        Returns:
            Tuple of (feedback_signal, confidence).
        """
        confidence = 0.6  # Lower confidence for implicit signals
        
        if action == "dismissed":
            return "implicit_disagree", confidence
        elif action == "spent_time":
            if time_spent and time_spent > 180:  # >3 min = strong signal
                return "implicit_agree", 0.8
            return "implicit_agree", confidence
        elif action == "returned":
            return "implicit_strong_agree", 0.85
        else:
            return "neutral", 0.3
    
    def aggregate_feedback_signal(self, feedback_list: List[UserFeedback]) -> Dict[str, float]:
        """Aggregate multiple feedback signals.
        
        Args:
            feedback_list: List of feedback objects.
        
        Returns:
            Aggregated signal dict with "direction" and "confidence".
        """
        if not feedback_list:
            return {"direction": "neutral", "weighted_signal": 0.0, "confidence": 0.0}
        
        total_weight = 0.0
        weighted_signal = 0.0
        
        for feedback in feedback_list:
            if feedback.rating is not None:
                weight = 1.0  # Explicit has full weight
                signal = feedback.rating  # -1, 0, or +1
                weighted_signal += signal * weight
                total_weight += weight
        
        if total_weight == 0:
            return {"direction": "neutral", "weighted_signal": 0.0, "confidence": 0.0}
        
        avg_signal = weighted_signal / total_weight
        confidence = min(1.0, len(feedback_list) / 5.0)  # Confidence grows with count
        
        if avg_signal > 0.3:
            direction = "user_disagrees_with_decision"
        elif avg_signal < -0.3:
            direction = "user_agrees_with_decision"
        else:
            direction = "neutral"
        
        return {
            "direction": direction,
            "weighted_signal": avg_signal,
            "confidence": confidence,
        }
    
    def estimate_decision_accuracy(self, feedback_list: List[UserFeedback]) -> float:
        """Estimate how accurate the system's decisions are based on feedback.
        
        Args:
            feedback_list: Historical feedback.
        
        Returns:
            Accuracy score 0-1.
        """
        if not feedback_list:
            return 0.5
        
        correct_count = 0
        for feedback in feedback_list:
            if feedback.rating == 0:  # User neutral = correct decision
                correct_count += 1
            elif feedback.rating == 1 or feedback.rating == -1:
                # Counted as partially correct if feedback provided
                correct_count += 0.5
        
        return correct_count / len(feedback_list)
    
    def extract_learning_signal(self, decision_outcome: Dict) -> Dict[str, float]:
        """Extract learning signal from decision outcome and feedback.
        
        Args:
            decision_outcome: Dict with decision info and feedback.
        
        Returns:
            Learning signal dict.
        """
        learning_signal = {
            "value_alignment_adjustment": 0.0,
            "confidence_adjustment": 0.0,
            "rule_firing_efficacy": 0.0,
        }
        
        feedback = decision_outcome.get("feedback")
        if not feedback:
            return learning_signal
        
        # If explicit feedback, adjust value alignment confidence
        if feedback.rating is not None:
            if feedback.rating == 0:
                learning_signal["confidence_adjustment"] = 0.05
            else:
                learning_signal["confidence_adjustment"] = -0.05  # Reduce confidence
        
        # If implicit engagement is strong, boost confidence
        if feedback.time_spent_seconds and feedback.time_spent_seconds > 300:
            learning_signal["confidence_adjustment"] = 0.03
        
        return learning_signal
    
    def detect_user_goal_drift(self, value_history: List[ValueProfile],
                              threshold: float = 0.15) -> bool:
        """Detect if user values are drifting significantly.
        
        Args:
            value_history: Historical value profiles (chronological).
            threshold: Maximum allowed change per value.
        
        Returns:
            True if drift detected.
        """
        if len(value_history) < 2:
            return False
        
        old_values = value_history[0].values
        new_values = value_history[-1].values
        
        max_change = 0.0
        for category in old_values:
            if category in new_values:
                for dim in old_values[category]:
                    if dim in new_values[category]:
                        change = abs(new_values[category][dim] - old_values[category][dim])
                        max_change = max(max_change, change)
        
        if max_change > threshold:
            logger.warning(f"User value drift detected: max_change={max_change:.2f}")
            return True
        
        return False
    
    def recommend_value_update_schedule(self, feedback_count: int,
                                       days_since_update: int) -> Dict[str, any]:
        """Recommend when next values update should occur.
        
        Args:
            feedback_count: Number of feedback signals received.
            days_since_update: Days since last values update.
        
        Returns:
            Recommendation dict.
        """
        # Update if we have 10+ feedback signals or every 7 days
        should_update = feedback_count >= 10 or days_since_update >= 7
        
        days_until_update = 7 - days_since_update
        feedback_until_update = 10 - feedback_count
        
        return {
            "should_update": should_update,
            "next_update_in_days": max(0, days_until_update),
            "feedback_signals_needed": max(0, feedback_until_update),
            "update_priority": "high" if should_update else "normal",
        }
