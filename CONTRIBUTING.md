# 🔥 Contributing to Phaethon

Thank you for your interest in contributing to Phaethon! This guide will help you understand how to extend and improve the system.

## Architecture Overview for Contributors

### Core Components

**Learning System** → **Scoring System** → **Decision Engine** → **Action**

1. **Learning**: Infers user values from feedback and behavior
2. **Scoring**: Evaluates content against those values
3. **Decisions**: Decides what action to take
4. **Adapters**: Execute decisions in external systems

---

## Extension Points

### 1. Custom Value Dimensions

Add new dimensions to the value hierarchy:

**Example: Adding "creativity" value**

```python
# In phaethon/config.py
DEFAULT_VALUE_HIERARCHY = {
    ...
    "creativity": ["self_expression", "novelty", "artistic_growth"],
}
```

Then update the scorer to incorporate:

```python
# In phaethon/scoring/scorer.py
def _calculate_value_alignment(self, content, features, values):
    ...
    if "self_expression" in values.get("creativity", {}):
        creativity_value = values["creativity"]["self_expression"]
        # Content with high creativity scores
        is_creative = any(
            topic in ["art", "music", "writing", "design"] 
            for topic in features.main_topics
        )
        creativity_alignment = 0.9 if is_creative else 0.2
        scores["self_expression"] = creativity_value * creativity_alignment
```

### 2. Custom Scoring Rules

Extend the ContentScorer for domain-specific logic:

```python
# custom_scorer.py
from phaethon.scoring.scorer import ContentScorer

class AcademiaScorer(ContentScorer):
    """Custom scorer for academic content."""
    
    def _calculate_value_alignment(self, content, features, values):
        scores = super()._calculate_value_alignment(content, features, values)
        
        # Boost score for peer-reviewed content
        if "arxiv.org" in content.domain or "Scholar.google.com" in content.domain:
            scores["rigor"] = 0.95
        
        # Penalize predatory journals
        if content.domain in PREDATORY_JOURNALS:
            scores["rigor"] = 0.1
        
        return scores
```

### 3. Custom Adapters

Create adapters to integrate with new systems:

```python
# phaethon/adapters/slack_adapter.py
from phaethon.adapters import BaseAdapter
from phaethon.server.app import app
from phaethon import decision_engine

class SlackAdapter(BaseAdapter):
    """Filters Slack links based on Phaethon values."""
    
    def __init__(self, bot_token: str):
        super().__init__()
        self.token = bot_token
    
    async def start(self):
        """Start Slack bot."""
        from slack_bolt.async_app import AsyncApp
        self.app = AsyncApp(token=self.token)
        
        @self.app.message()
        async def handle_link(body, say):
            # Extract URL from message
            url = self._extract_url(body["text"])
            
            # Evaluate with Phaethon
            decision = await self._evaluate_content(url)
            
            # Take action
            if decision.decision == InterventionAction.BLOCK:
                await say(
                    f"⚠️ This content is blocked (misaligned with your values)\n"
                    f"Reason: {decision.reasoning}"
                )
    
    async def stop(self):
        """Stop Slack bot."""
        pass
    
    async def health_check(self) -> bool:
        return True
    
    async def _evaluate_content(self, url: str):
        # Call Phaethon API to evaluate
        pass
```

### 4. Custom Learning Algorithms

Enhance the values inference with new learning methods:

```python
# phaethon/learning/advanced_estimator.py
from phaethon.learning.values_estimator import BayesianValuesEstimator
from phaethon.core.schemas import ValueProfile, UserFeedback

class ReinforcementValuesEstimator(BayesianValuesEstimator):
    """Uses reinforcement learning for value updates."""
    
    def __init__(self, learning_rate: float = 0.01):
        super().__init__()
        self.learning_rate = learning_rate
    
    def update_from_feedback(self, current_values, feedback, value_mapping):
        """Update using Q-learning instead of Bayesian."""
        
        # Calculate reward signal
        reward = feedback.rating  # -1, 0, or 1
        
        # Q-learning update for each value
        updated_values = {}
        for category, dimensions in current_values.values.items():
            updated_values[category] = {}
            for dim, current_score in dimensions.items():
                # Q-learning: V_new = V_old + α * (reward - V_old)
                new_score = current_score + self.learning_rate * (reward - current_score)
                updated_values[category][dim] = max(0.0, min(1.0, new_score))
        
        return ValueProfile(
            values=updated_values,
            confidence=min(0.95, current_values.confidence + 0.02),
        )
```

### 5. Custom Decision Logic

Modify the decision engine for special cases:

```python
# custom_decision.py
from phaethon.intervention.decision_engine import DecisionEngine
from phaethon.core.schemas import InterventionAction

class ContextAwareDecisionEngine(DecisionEngine):
    """Makes decisions based on time/context (e.g., work hours only)."""
    
    def __init__(self, work_hours: tuple = (9, 17)):
        super().__init__()
        self.work_start, self.work_end = work_hours
    
    def make_decision(self, content, user_profile, scoring_result):
        from datetime import datetime
        
        decision = super().make_decision(content, user_profile, scoring_result)
        
        # During work hours, be stricter
        now = datetime.now()
        is_work_hours = self.work_start <= now.hour < self.work_end
        
        if is_work_hours and decision.decision == InterventionAction.ALLOW:
            # Downgrade to ALLOW_MUTE
            decision.decision = InterventionAction.ALLOW_MUTE
            decision.reasoning += " (Muted during work hours)"
        
        return decision
```

---

## Testing Your Extensions

### Unit Tests

```python
# tests/test_custom_scorer.py
import pytest
from custom_scorer import AcademiaScorer

def test_arxiv_boosted():
    """Test that arxiv papers get high rigor scores."""
    scorer = AcademiaScorer()
    
    content = ContentItem(
        content_id="paper-1",
        source="https://arxiv.org/paper.pdf",
        title="Important Research",
        content_type=ContentType.ARTICLE,
        domain="arxiv.org",
    )
    
    profile = UserProfile(user_id="researcher-1", ...)
    result = scorer.score_content(content, profile)
    
    assert result.scores_by_value.get("rigor", 0) > 0.9
```

### Integration Tests

```python
# Test with the real API
import requests

def test_adapter_integration():
    """Test adapter with running Phaethon server."""
    # Start adapter
    adapter = SlackAdapter(bot_token="xoxb-...")
    asyncio.run(adapter.start())
    
    # Verify it's working
    assert await adapter.health_check()
    
    # Clean up
    asyncio.run(adapter.stop())
```

---

## Coding Standards

### Style

We follow PEP 8 with some additions:

```python
# Good: Clear, type-hinted functions
def score_content(self, content: ContentItem, user_profile: UserProfile) -> ScoringResult:
    """Score content against user values.
    
    Args:
        content: ContentItem to score.
        user_profile: User's profile with values.
    
    Returns:
        ScoringResult with detailed scoring.
    """
    pass

# Bad: Unclear, no types
def score(self, c, p):
    """Score it."""
    pass
```

### Documentation

Every class and method should have:
1. Docstring explaining purpose
2. Args and Returns documented
3. Example usage in docstring (for complex functions)

### Performance

- Keep score computation < 100ms per content item
- Batch database operations when possible
- Use async for I/O-bound operations

---

## Pull Request Process

1. **Fork** the repository
2. **Branch** from `main` with a descriptive name: `feature/custom-scorer`
3. **Implement** your feature with tests
4. **Test** with `pytest tests/ -v`
5. **Document** all changes
6. **Submit** PR with description of changes

### PR Checklist

- [ ] Tests written and passing
- [ ] Code follows PEP 8
- [ ] Docstrings added
- [ ] No breaking changes to public API
- [ ] Documentation updated

---

## Architecture for Extension

### How Data Flows

```
User Feedback
    ↓
[Learning System] → ValueProfile
    ↓
Content Item
    ↓
[Scoring System] → ScoringResult
    ↓
[Decision Engine] → InterventionDecision
    ↓
[Adapter] → Action (block, prioritize, warn, etc.)
    ↓
External System (Browser, Proxy, App)
```

### Where to Add What

**New Value Type?** → Add to `DEFAULT_VALUE_HIERARCHY` in config.py

**Improve Scoring?** → Subclass `ContentScorer` 

**New Integration?** → Create adapter in `phaethon/adapters/`

**Better Learning?** → Extend `BayesianValuesEstimator`

**Special Decisions?** → Subclass `DecisionEngine`

---

## Examples in the Codebase

Good examples to learn from:

- `phaethon/scoring/scorer.py` - How scoring works
- `phaethon/learning/values_estimator.py` - Bayesian updating
- `phaethon/intervention/decision_engine.py` - Decision logic
- `tests/test_scoring.py` - How to write tests

---

## Getting Help

- **Questions?** Open a GitHub Discussion
- **Bug?** File an Issue with reproducible example
- **Feature?** Submit an Issue describing desired feature
- **Code Review?** We'll help with design feedback

---

## Roadmap

We're actively working on:

1. **Phase 2**: Browser Extension Adapter
2. **Phase 3**: Advanced ML Scoring (embeddings)
3. **Phase 4**: Reinforcement Learning for Weighting
4. **Phase 5**: Multi-Adapter Ecosystem

Great areas to contribute:

- Browser extension implementation
- Semantic content analysis
- Additional adapters (Slack, Teams, Discord, etc.)
- Mobile app integration
- Advanced analytics dashboard

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're building something to help protect human attention and values—let's keep it civilized.

---

Thank you for contributing to Phaethon! 🔥
