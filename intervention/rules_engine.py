"""User intervention rules engine."""

import logging
from typing import List, Dict, Optional, Tuple

from ..core.schemas import ContentItem, InterventionRule, InterventionAction

logger = logging.getLogger(__name__)


class RulesEngine:
    """Evaluates user-defined intervention rules."""
    
    def evaluate_rules(self, content: ContentItem, rules: List[InterventionRule]) -> Tuple[Optional[InterventionAction], Optional[InterventionRule]]:
        """Evaluate all active rules against content.
        
        Args:
            content: ContentItem to check against rules.
            rules: List of InterventionRules to evaluate.
        
        Returns:
            Tuple of (action, triggering_rule) or (None, None) if no rules match.
            Returns highest-priority matching rule.
        """
        matching_rules = []
        
        for rule in rules:
            if not rule.is_active:
                continue
            
            if self._rule_matches(rule, content):
                matching_rules.append(rule)
        
        if not matching_rules:
            return None, None
        
        # Return highest priority rule
        best_rule = max(matching_rules, key=lambda r: r.priority)
        return best_rule.action, best_rule
    
    def _rule_matches(self, rule: InterventionRule, content: ContentItem) -> bool:
        """Check if rule matches the content.
        
        Args:
            rule: Rule to check.
            content: Content to match against.
        
        Returns:
            True if rule matches.
        """
        # Check domain
        if rule.domain and rule.domain.lower() not in content.domain.lower():
            return False
        
        # Check content type
        if rule.content_type and rule.content_type != content.content_type:
            return False
        
        # Check keyword includes (content must match at least one)
        if rule.keyword_includes:
            title_lower = content.title.lower()
            if not any(kw.lower() in title_lower for kw in rule.keyword_includes):
                return False
        
        # Check keyword excludes (must not match any)
        if rule.keyword_excludes:
            title_lower = content.title.lower()
            if any(kw.lower() in title_lower for kw in rule.keyword_excludes):
                return False
        
        return True
    
    def get_matching_rules(self, content: ContentItem, rules: List[InterventionRule]) -> List[InterventionRule]:
        """Get all matching rules for content (sorted by priority).
        
        Args:
            content: ContentItem to check.
            rules: List of rules.
        
        Returns:
            List of matching rules sorted by priority (highest first).
        """
        matching = [r for r in rules if self._rule_matches(r, content) and r.is_active]
        return sorted(matching, key=lambda r: r.priority, reverse=True)
    
    def validate_rule(self, rule: InterventionRule) -> Tuple[bool, Optional[str]]:
        """Validate a rule for correctness.
        
        Args:
            rule: Rule to validate.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        if not rule.rule_id:
            return False, "rule_id is required"
        
        if not isinstance(rule.action, InterventionAction):
            return False, f"Invalid action: {rule.action}"
        
        if not rule.reason:
            return False, "reason is required"
        
        if rule.priority < 0 or rule.priority > 100:
            return False, "priority must be 0-100"
        
        return True, None
