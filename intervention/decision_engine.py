"""Intervention decision engine."""

import logging
import uuid
from datetime import datetime
from typing import Dict, Tuple, Optional

from ..core.schemas import (
    ContentItem,
    UserProfile,
    ScoringResult,
    InterventionDecision,
    InterventionAction,
)
from .rules_engine import RulesEngine

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Makes intervention decisions based on scores and rules."""
    
    def __init__(self):
        """Initialize decision engine."""
        self.rules_engine = RulesEngine()
    
    def make_decision(self, content: ContentItem, user_profile: UserProfile,
                     scoring_result: ScoringResult) -> InterventionDecision:
        """Make intervention decision for content.
        
        Args:
            content: ContentItem to decide on.
            user_profile: User's profile.
            scoring_result: Pre-computed scoring result.
        
        Returns:
            InterventionDecision with action and reasoning.
        """
        # Step 1: Check explicit user rules (override score if match)
        rule_action, matched_rule = self.rules_engine.evaluate_rules(
            content, user_profile.rules
        )
        
        applied_rules = []
        if matched_rule:
            applied_rules.append({
                "rule_id": matched_rule.rule_id,
                "weight": 1.0,
                "reason": matched_rule.reason,
                "action": matched_rule.action.value,
            })
        
        # Step 2: If rule matches, use rule action; otherwise use scored action
        if rule_action:
            final_action = rule_action
            reasoning = f"User rule '{matched_rule.reason}' matched this content: {matched_rule.action.value}"
        else:
            final_action = self._choose_action_from_score(scoring_result, user_profile)
            reasoning = scoring_result.reasoning
        
        # Step 3: Apply safety constraints
        final_action = self._apply_safety_constraints(final_action, user_profile, scoring_result)
        
        # Create decision object
        decision = InterventionDecision(
            decision_id=str(uuid.uuid4()),
            content_id=content.content_id,
            user_id=user_profile.user_id,
            decision=final_action,
            scores=scoring_result,
            applied_rules=applied_rules,
            reasoning=reasoning,
            timestamp=datetime.utcnow(),
        )
        
        logger.info(f"Decision: {final_action.value} for {content.title[:50]}")
        return decision
    
    def _choose_action_from_score(self, scoring: ScoringResult, 
                                  user_profile: UserProfile) -> InterventionAction:
        """Choose intervention action based on scoring result.
        
        Args:
            scoring: ScoringResult with scores and recommended action.
            user_profile: User profile (for preferences).
        
        Returns:
            InterventionAction to take.
        """
        # Start with recommended action from scorer
        action = scoring.recommended_action
        
        # Adjust based on user preferences
        if not user_profile.preferences.enable_implicit_feedback:
            # More conservative if we can't learn from feedback
            if action == InterventionAction.ALLOW_MUTE:
                action = InterventionAction.ALLOW_WARNING
        
        return action
    
    def _apply_safety_constraints(self, action: InterventionAction,
                                 user_profile: UserProfile,
                                 scoring: ScoringResult) -> InterventionAction:
        """Apply safety constraints to action.
        
        Args:
            action: Proposed action.
            user_profile: User profile.
            scoring: Scoring result.
        
        Returns:
            Possibly modified action for safety.
        """
        # Never block if wellbeing impact is neutral or positive
        if action == InterventionAction.BLOCK and scoring.wellbeing_impact > -0.1:
            return InterventionAction.ALLOW_WARNING
        
        return action
    
    def explain_decision(self, decision: InterventionDecision) -> Dict[str, any]:
        """Generate detailed explanation of decision.
        
        Args:
            decision: InterventionDecision to explain.
        
        Returns:
            Dict with detailed explanation.
        """
        explanation = {
            "action": decision.decision.value,
            "summary": decision.reasoning,
            "scoring": {
                "alignment": f"{decision.scores.alignment_score:.0%}",
                "productivity_impact": f"{decision.scores.productivity_impact:+.0%}",
                "wellbeing_impact": f"{decision.scores.wellbeing_impact:+.0%}",
                "confidence": f"{decision.scores.confidence:.0%}",
            },
            "value_scores": {
                k: f"{v:.0%}" for k, v in decision.scores.scores_by_value.items()
            },
            "applied_rules": decision.applied_rules,
        }
        
        return explanation
