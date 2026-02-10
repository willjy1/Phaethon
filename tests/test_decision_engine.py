"""Unit tests for decision and intervention engines."""

import pytest
from phaethon.core.schemas import (
    ContentItem,
    ContentType,
    UserProfile,
    ValueProfile,
    InterventionRule,
    InterventionAction,
    ScoringResult,
)
from phaethon.intervention.rules_engine import RulesEngine
from phaethon.intervention.decision_engine import DecisionEngine


class TestRulesEngine:
    """Test rules evaluation."""
    
    def setup_method(self):
        """Setup for each test."""
        self.engine = RulesEngine()
    
    def test_rule_matches_domain(self):
        """Test domain matching rule."""
        rule = InterventionRule(
            rule_id="rule-1",
            domain="twitter.com",
            action=InterventionAction.BLOCK,
            reason="Too distracting",
        )
        
        content = ContentItem(
            content_id="post-1",
            source="https://twitter.com/post",
            title="Random post",
            content_type=ContentType.SOCIAL_POST,
            domain="twitter.com",
        )
        
        matches = self.engine._rule_matches(rule, content)
        assert matches
    
    def test_rule_matches_keywords(self):
        """Test keyword matching rule."""
        rule = InterventionRule(
            rule_id="rule-2",
            keyword_includes=["productivity", "focus"],
            action=InterventionAction.ALLOW_PRIORITIZE,
            reason="Relevant to my goals",
        )
        
        content = ContentItem(
            content_id="article-1",
            source="https://example.com/article",
            title="How to Improve Your Productivity and Focus",
            content_type=ContentType.ARTICLE,
            domain="example.com",
        )
        
        matches = self.engine._rule_matches(rule, content)
        assert matches
    
    def test_evaluate_rules_returns_highest_priority(self):
        """Test that highest priority rule is returned."""
        rules = [
            InterventionRule(
                rule_id="rule-1",
                domain="twitter.com",
                action=InterventionAction.BLOCK,
                reason="Block all Twitter",
                priority=50,
            ),
            InterventionRule(
                rule_id="rule-2",
                domain="twitter.com",
                keyword_includes=["work"],
                action=InterventionAction.ALLOW,
                reason="Allow work-related Twitter",
                priority=90,
            ),
        ]
        
        content = ContentItem(
            content_id="post-1",
            source="https://twitter.com/work-post",
            title="Work-related content about project",
            content_type=ContentType.SOCIAL_POST,
            domain="twitter.com",
        )
        
        action, rule = self.engine.evaluate_rules(content, rules)
        
        assert action == InterventionAction.ALLOW
        assert rule.priority == 90


class TestDecisionEngine:
    """Test decision making."""
    
    def setup_method(self):
        """Setup for each test."""
        self.engine = DecisionEngine()
    
    def test_decision_respects_user_rules(self):
        """Test that user rules override scores."""
        rule = InterventionRule(
            rule_id="rule-1",
            domain="twitter.com",
            action=InterventionAction.BLOCK,
            reason="No Twitter",
            priority=100,
        )
        
        profile = UserProfile(
            user_id="user-1",
            rules=[rule],
            values=ValueProfile(
                values={"productivity": {"focus": 0.95}},
                confidence=0.85,
            )
        )
        
        content = ContentItem(
            content_id="post-1",
            source="https://twitter.com/post",
            title="Some post",
            content_type=ContentType.SOCIAL_POST,
            domain="twitter.com",
        )
        
        scoring = ScoringResult(
            content_id="post-1",
            user_id="user-1",
            alignment_score=0.5,
            productivity_impact=0.2,
            wellbeing_impact=0.1,
            confidence=0.8,
            reasoning="Medium alignment",
            recommended_action=InterventionAction.ALLOW,
        )
        
        decision = self.engine.make_decision(content, profile, scoring)
        
        # Rule should override score
        assert decision.decision == InterventionAction.BLOCK
    
    def test_explain_decision(self):
        """Test decision explanation."""
        from phaethon.core.schemas import InterventionDecision
        
        scoring = ScoringResult(
            content_id="article-1",
            user_id="user-1",
            alignment_score=0.85,
            productivity_impact=0.7,
            wellbeing_impact=0.2,
            confidence=0.9,
            scores_by_value={"learning": 0.9, "focus": 0.8},
            reasoning="High-quality learning content",
            recommended_action=InterventionAction.ALLOW_PRIORITIZE,
        )
        
        decision = InterventionDecision(
            decision_id="decision-1",
            content_id="article-1",
            user_id="user-1",
            decision=InterventionAction.ALLOW_PRIORITIZE,
            scores=scoring,
            reasoning="High-quality learning content",
        )
        
        explanation = self.engine.explain_decision(decision)
        
        assert explanation["action"] == "ALLOW_PRIORITIZE"
        assert "learning" in explanation["value_scores"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
