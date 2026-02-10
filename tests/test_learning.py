"""Unit tests for values learning and inference."""

import pytest
from phaethon.core.schemas import (
    ValueProfile,
    UserFeedback,
    FeedbackType,
)
from phaethon.learning.values_estimator import BayesianValuesEstimator
from phaethon.learning.feedback_processor import FeedbackProcessor
from phaethon.learning.behavioral_patterns import BehavioralAnalyzer


class TestBayesianValuesEstimator:
    """Test Bayesian values estimation."""
    
    def setup_method(self):
        """Setup for each test."""
        self.estimator = BayesianValuesEstimator()
    
    def test_initialize_values(self):
        """Test values initialization."""
        hierarchy = {
            "productivity": ["focus", "learning"],
            "wellbeing": ["sleep", "health"],
        }
        
        profile = self.estimator.initialize_values(hierarchy)
        
        assert "productivity" in profile.values
        assert "focus" in profile.values["productivity"]
        assert profile.values["productivity"]["focus"] == 0.5  # Uniform prior
        assert profile.confidence == 0.0  # Low confidence initially
    
    def test_update_from_explicit_feedback(self):
        """Test updating values from user feedback."""
        initial_values = ValueProfile(
            values={"productivity": {"focus": 0.5}},
            confidence=0.3,
        )
        
        feedback = UserFeedback(
            decision_id="decision-1",
            user_id="user-1",
            feedback_type=FeedbackType.EXPLICIT_RATING,
            rating=1,  # User says we were too strict
        )
        
        updated = self.estimator.update_from_feedback(
            initial_values,
            feedback,
            {"productivity": ["focus"]},
        )
        
        # Feedback that we were too strict should slightly decrease focus value
        assert updated.values["productivity"]["focus"] < initial_values.values["productivity"]["focus"]
        assert updated.confidence > initial_values.confidence
    
    def test_confidence_increases_with_feedback(self):
        """Test that confidence increases with multiple feedbacks."""
        profile = ValueProfile(values={"productivity": {"focus": 0.5}}, confidence=0.1)
        
        # Multiple feedback rounds
        for i in range(5):
            feedback = UserFeedback(
                decision_id=f"decision-{i}",
                user_id="user-1",
                feedback_type=FeedbackType.EXPLICIT_RATING,
                rating=0,
            )
            profile = self.estimator.update_from_feedback(
                profile,
                feedback,
                {"productivity": ["focus"]},
            )
        
        assert profile.confidence > 0.1


class TestFeedbackProcessor:
    """Test feedback processing."""
    
    def setup_method(self):
        """Setup for each test."""
        self.processor = FeedbackProcessor()
    
    def test_process_explicit_feedback(self):
        """Test processing explicit feedback."""
        feedback_agree = UserFeedback(
            decision_id="decision-1",
            user_id="user-1",
            feedback_type=FeedbackType.EXPLICIT_RATING,
            rating=0,
        )
        
        signal, confidence = self.processor.process_explicit_feedback(feedback_agree)
        assert confidence > 0.8
    
    def test_process_implicit_feedback(self):
        """Test processing implicit engagement feedback."""
        # Long engagement = strong positive signal
        signal, confidence = self.processor.process_implicit_feedback(
            action="spent_time",
            time_spent=300,  # 5 minutes
        )
        
        assert signal == "implicit_agree"
        assert confidence > 0.7
    
    def test_aggregate_feedback_signals(self):
        """Test aggregating multiple feedback signals."""
        feedbacks = [
            UserFeedback(decision_id="d1", user_id="u1", feedback_type=FeedbackType.EXPLICIT_RATING, rating=1),
            UserFeedback(decision_id="d2", user_id="u1", feedback_type=FeedbackType.EXPLICIT_RATING, rating=1),
            UserFeedback(decision_id="d3", user_id="u1", feedback_type=FeedbackType.EXPLICIT_RATING, rating=0),
        ]
        
        aggregated = self.processor.aggregate_feedback_signal(feedbacks)
        
        assert "direction" in aggregated
        assert "confidence" in aggregated


class TestBehavioralAnalyzer:
    """Test behavioral pattern analysis."""
    
    def setup_method(self):
        """Setup for each test."""
        self.analyzer = BehavioralAnalyzer()
    
    def test_analyze_time_of_day_patterns(self):
        """Test time-of-day pattern analysis."""
        from datetime import datetime, timedelta
        
        history = [
            {
                "timestamp": datetime.utcnow().replace(hour=9),
                "engagement_score": 0.9,
            },
            {
                "timestamp": datetime.utcnow().replace(hour=14),
                "engagement_score": 0.5,
            },
            {
                "timestamp": datetime.utcnow().replace(hour=21),
                "engagement_score": 0.3,
            },
        ]
        
        patterns = self.analyzer.analyze_time_of_day_patterns(history)
        
        assert 9 in patterns
        assert patterns[9] > patterns[21]  # More engaged in morning
    
    def test_analyze_content_type_preferences(self):
        """Test content type preference analysis."""
        history = [
            {"content_type": "article", "engagement_score": 0.9},
            {"content_type": "article", "engagement_score": 0.85},
            {"content_type": "video", "engagement_score": 0.3},
        ]
        
        preferences = self.analyzer.analyze_content_type_preferences(history)
        
        assert preferences["article"] > preferences["video"]
    
    def test_detect_attention_fragmentation(self):
        """Test attention fragmentation detection."""
        # Many short interactions = fragmented attention
        history = [
            {"time_spent": 10},
            {"time_spent": 15},
            {"time_spent": 12},
            {"time_spent": 8},
            {"time_spent": 20},
        ]
        
        avg_per_item = sum(h["time_spent"] for h in history) / len(history)
        assert avg_per_item < 30
        
        fragmentation = self.analyzer.detect_attention_fragmentation(history)
        assert fragmentation > 0.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
