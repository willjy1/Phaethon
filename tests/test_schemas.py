"""Unit tests for Phaethon's core data models and schemas."""

import pytest
from datetime import datetime

from phaethon.core.schemas import (
    ContentItem,
    ContentType,
    ContentMetadata,
    InterventionAction,
    ValueProfile,
    UserProfile,
    ScoringResult,
    InterventionRule,
    UserFeedback,
    FeedbackType,
)


class TestContentItem:
    """Test ContentItem model."""
    
    def test_create_content_item(self):
        """Test creating a content item."""
        content = ContentItem(
            content_id="test-1",
            source="https://example.com/article",
            title="Test Article",
            content_type=ContentType.ARTICLE,
            domain="example.com",
        )
        
        assert content.content_id == "test-1"
        assert content.title == "Test Article"
        assert content.domain == "example.com"
    
    def test_content_item_with_metadata(self):
        """Test content item with metadata."""
        metadata = ContentMetadata(
            author="John Doe",
            topics=["AI", "Learning"],
            language="en",
        )
        
        content = ContentItem(
            content_id="test-2",
            source="https://example.com/article",
            title="Test Article",
            content_type=ContentType.ARTICLE,
            domain="example.com",
            metadata=metadata,
        )
        
        assert content.metadata.author == "John Doe"
        assert "AI" in content.metadata.topics


class TestValueProfile:
    """Test ValueProfile model."""
    
    def test_create_value_profile(self):
        """Test creating a value profile."""
        values = {
            "productivity": {
                "focus": 0.95,
                "learning": 0.85,
            },
            "wellbeing": {
                "sleep": 0.90,
            }
        }
        
        profile = ValueProfile(
            values=values,
            confidence=0.85,
        )
        
        assert profile.values["productivity"]["focus"] == 0.95
        assert profile.confidence == 0.85


class TestUserProfile:
    """Test UserProfile model."""
    
    def test_create_user_profile(self):
        """Test creating a user profile."""
        profile = UserProfile(
            user_id="user-1",
        )
        
        assert profile.user_id == "user-1"
        assert profile.total_content_processed == 0
        assert profile.total_decisions_made == 0
    
    def test_user_profile_with_rules(self):
        """Test user profile with intervention rules."""
        rule = InterventionRule(
            rule_id="rule-1",
            domain="twitter.com",
            action=InterventionAction.BLOCK,
            reason="Too distracting",
        )
        
        profile = UserProfile(
            user_id="user-1",
            rules=[rule],
        )
        
        assert len(profile.rules) == 1
        assert profile.rules[0].domain == "twitter.com"


class TestScoringResult:
    """Test ScoringResult model."""
    
    def test_create_scoring_result(self):
        """Test creating a scoring result."""
        result = ScoringResult(
            content_id="content-1",
            user_id="user-1",
            alignment_score=0.85,
            productivity_impact=0.5,
            wellbeing_impact=-0.1,
            confidence=0.90,
            reasoning="High-quality learning content",
            recommended_action=InterventionAction.ALLOW_PRIORITIZE,
        )
        
        assert result.alignment_score == 0.85
        assert result.confidence == 0.90
        assert result.recommended_action == InterventionAction.ALLOW_PRIORITIZE


class TestInterventionRule:
    """Test InterventionRule model."""
    
    def test_create_rule(self):
        """Test creating an intervention rule."""
        rule = InterventionRule(
            rule_id="rule-1",
            domain="reddit.com",
            action=InterventionAction.BLOCK,
            reason="Procrastination trigger",
            priority=50,
        )
        
        assert rule.rule_id == "rule-1"
        assert rule.domain == "reddit.com"
        assert rule.priority == 50
    
    def test_rule_with_keywords(self):
        """Test rule with keyword matching."""
        rule = InterventionRule(
            rule_id="rule-2",
            keyword_includes=["productivity", "focus"],
            action=InterventionAction.ALLOW_PRIORITIZE,
            reason="Relevant to my goals",
        )
        
        assert "productivity" in rule.keyword_includes
        assert rule.action == InterventionAction.ALLOW_PRIORITIZE


class TestUserFeedback:
    """Test UserFeedback model."""
    
    def test_create_feedback(self):
        """Test creating user feedback."""
        feedback = UserFeedback(
            decision_id="decision-1",
            user_id="user-1",
            feedback_type=FeedbackType.EXPLICIT_RATING,
            rating=1,  # Too strict
            comment="I actually wanted to see that article",
        )
        
        assert feedback.rating == 1
        assert feedback.feedback_type == FeedbackType.EXPLICIT_RATING
    
    def test_engagement_feedback(self):
        """Test engagement-based feedback."""
        feedback = UserFeedback(
            decision_id="decision-1",
            user_id="user-1",
            feedback_type=FeedbackType.ENGAGEMENT,
            action_taken="spent_time",
            time_spent_seconds=420,  # 7 minutes
        )
        
        assert feedback.action_taken == "spent_time"
        assert feedback.time_spent_seconds == 420


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
