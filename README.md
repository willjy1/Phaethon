# 🔥 Phaethon: Attention Firewall

[![CI](https://github.com/willjy1/Phaethon/actions/workflows/ci.yml/badge.svg)](https://github.com/willjy1/Phaethon/actions/workflows/ci.yml)

An intelligent attention firewall that learns your higher-order productive values and curates your entire digital experience accordingly by blocking misaligned content and prioritizing aligned content.

## 🎯 Vision

In an attention economy designed to capture and exploit your focus, **Phaethon** becomes your values-aligned sentinel. It learns what truly matters to you—not from explicit lists, but from your behavior, feedback, and stated goals. Then it intelligently filters your digital world:

- **Blocks** content misaligned with your values
- **Prioritizes** content that advances your goals  
- **Warns** about potentially problematic content
- **Learns** continuously from your feedback and behavior

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Extension Development](#extension-development)

---

## 🏗️ Architecture Overview

Phaethon is built from four core pillars:

### 1. **Values Inference Engine** 🧠
Learns your productive values through:
- Bayesian inference on user feedback
- Behavioral pattern analysis
- Engagement metrics
- Explicit goal statements

Produces: `ValueProfile` with confidence scores for each value dimension.

### 2. **Content Scoring System** 📊
Evaluates every piece of content against your values:
- Feature extraction (topics, tone, source quality)
- Multi-dimensional alignment scoring
- Productivity/wellbeing impact estimation
- Confidence quantification

Produces: `ScoringResult` with detailed reasoning.

### 3. **Intervention Engine** 🛡️
Makes real-time filtering decisions:
- User-defined rule evaluation (highest priority)
- Scoring-based recommendations
- Safety constraint application
- Explainable decision reasoning

Produces: `InterventionDecision` (BLOCK, ALLOW, ALLOW_PRIORITIZE, etc.)

### 4. **Feedback Loop & Learning** 🔄
Continuously improves through:
- Explicit user feedback (ratings)
- Implicit engagement signals

---

## 🧰 Developer Setup

Install pre-commit hooks and development dependencies locally:

```bash
python -m pip install -r requirements.txt
python -m pip install pre-commit
pre-commit install
```

Run the test suite:

```bash
pytest -q
```

Formatting/linting guidelines are enforced via `pre-commit` (Black, isort, Flake8).
- Value drift detection
- Periodic re-estimation

---

## 🚀 Quick Start

### Installation

```bash
cd phaethon

# Install dependencies
pip install -r requirements.txt

# Optional: Add to your Python path
pip install -e .
```

### Running the Server

```bash
# Start Phaethon on port 8001
python -m phaethon

# Or with uvicorn directly
uvicorn phaethon.server.app:app --port 8001 --reload
```

**Server starts at:** http://localhost:8001

### First API Call

```bash
# Initialize user
curl -X POST http://localhost:8001/api/values/initialize?user_id=user-1

# Evaluate content
curl -X POST http://localhost:8001/api/evaluate?user_id=user-1 \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "article-1",
    "source": "https://arxiv.org/paper",
    "title": "Deep Learning Paper Summary",
    "content_type": "article",
    "domain": "arxiv.org"
  }'
```

---

## 🔧 Core Components

### User Profile Management

```python
from phaethon.core.user_profile import UserProfileManager

manager = UserProfileManager()

# Create or get user
profile = manager.get_or_create_user("user-123")

# Update values
new_values = ValueProfile(
    values={
        "productivity": {
            "focus": 0.95,
            "learning": 0.87,
        }
    },
    confidence=0.8
)
manager.update_values("user-123", new_values)
```

### Values Inference

```python
from phaethon.learning.values_estimator import BayesianValuesEstimator

estimator = BayesianValuesEstimator()

# Initialize with hierarchy
hierarchy = {
    "productivity": ["focus", "learning", "output_quality"],
    "wellbeing": ["sleep_quality", "stress_management"],
}
values = estimator.initialize_values(hierarchy)

# Update from feedback
feedback = UserFeedback(
    decision_id="decision-1",
    user_id="user-1",
    feedback_type=FeedbackType.EXPLICIT_RATING,
    rating=1,  # "You were too strict"
)
updated_values = estimator.update_from_feedback(values, feedback, hierarchy)
```

### Content Scoring

```python
from phaethon.scoring.scorer import ContentScorer

scorer = ContentScorer()

content = ContentItem(
    content_id="article-1",
    source="https://example.com/article",
    title="How to Build a Personal Knowledge System",
    content_type=ContentType.ARTICLE,
    domain="example.com",
)

scoring = scorer.score_content(content, user_profile)
print(scoring)
# ScoringResult(
#     alignment_score=0.91,
#     productivity_impact=0.85,
#     wellbeing_impact=0.0,
#     recommended_action=InterventionAction.ALLOW_PRIORITIZE,
#     reasoning="High-value learning content matching learning value 0.87",
# )
```

### Decision Making

```python
from phaethon.intervention.decision_engine import DecisionEngine

decision_engine = DecisionEngine()

decision = decision_engine.make_decision(content, user_profile, scoring)
print(decision.decision)  # InterventionAction.ALLOW_PRIORITIZE

# Get detailed explanation
explanation = decision_engine.explain_decision(decision)
print(explanation["summary"])
```

---

## 📡 API Reference

### User Management

#### `POST /api/values/initialize`
Initialize user values with default hierarchy.

```json
{
  "user_id": "user-1"
}
```

Response:
```json
{
  "success": true,
  "values": {
    "productivity": {
      "focus": 0.5,
      "learning": 0.5,
      "output_quality": 0.5
    },
    "wellbeing": {
      "sleep_quality": 0.5,
      "stress_management": 0.5
    }
  }
}
```

#### `GET /api/profile?user_id=user-1`
Retrieve user profile with current values and rules.

Response:
```json
{
  "user_id": "user-1",
  "values": {
    "values": {...},
    "confidence": 0.75
  },
  "rules": [...],
  "stats": {
    "total_content_processed": 42,
    "total_decisions_made": 42,
    "active_rules": 3
  }
}
```

#### `POST /api/values/update`
Manually update values.

```json
{
  "values": {
    "productivity": {
      "focus": 0.95,
      "learning": 0.87
    },
    "wellbeing": {
      "sleep_quality": 0.92
    }
  },
  "confidence": 0.85
}
```

### Content Evaluation

#### `POST /api/evaluate`
Evaluate content and get intervention decision.

```json
{
  "content_id": "article-1",
  "source": "https://example.com/article",
  "title": "Learning Deep Neural Networks",
  "content_type": "article",
  "domain": "example.com"
}
```

Response:
```json
{
  "content_id": "article-1",
  "decision": "ALLOW_PRIORITIZE",
  "scoring": {
    "alignment_score": 0.91,
    "productivity_impact": 0.85,
    "wellbeing_impact": 0.1,
    "confidence": 0.87,
    "reasoning": "High-value learning content matching learning value 0.87"
  },
  "reasoning": "Recommended action: ALLOW_PRIORITIZE"
}
```

### Rules Management

#### `POST /api/rules`
Create an intervention rule.

```json
{
  "domain": "twitter.com",
  "action": "BLOCK",
  "reason": "Procrastination trigger",
  "priority": 75
}
```

#### `DELETE /api/rules/{rule_id}`
Delete a rule.

### Feedback

#### `POST /api/feedback`
Submit feedback on a decision.

```json
{
  "decision_id": "decision-1",
  "feedback_type": "explicit_rating",
  "rating": 1,
  "comment": "Actually I wanted to see that"
}
```

Response:
```json
{
  "success": true,
  "signal": "user_disagrees_with_decision",
  "confidence": 0.9
}
```

### Analytics

#### `GET /api/analytics/decision-stats?user_id=user-1`
Get decision statistics.

#### `GET /api/events?user_id=user-1&level=INFO&limit=100`
Get event log.

---

## ⚙️ Configuration

Edit [phaethon/config.py](phaethon/config.py) to customize:

```python
# Value hierarchy (what dimensions matter)
DEFAULT_VALUE_HIERARCHY = {
    "productivity": ["focus", "learning", "output_quality"],
    "wellbeing": ["sleep_quality", "stress_management"],
    ...
}

# Scoring thresholds
ALIGNMENT_SCORE_THRESHOLD = 0.6  # Below = consider blocking
PRODUCTIVITY_IMPACT_THRESHOLD = -0.3

# Update thresholds
MIN_FEEDBACK_FOR_VALUE_UPDATE = 10
DAYS_BETWEEN_VALUE_UPDATES = 7

# Server
API_HOST = "0.0.0.0"
API_PORT = 8001
```

---

## 🧪 Testing

### Run All Tests

```bash
cd phaethon
pytest tests/ -v
```

### Run Specific Tests

```bash
# Test schemas
pytest tests/test_schemas.py -v

# Test scoring
pytest tests/test_scoring.py -v

# Test decision engine
pytest tests/test_decision_engine.py -v

# Test learning
pytest tests/test_learning.py -v
```

### Example Test Run

```bash
$ pytest tests/ -v

tests/test_schemas.py::TestContentItem::test_create_content_item PASSED
tests/test_schemas.py::TestValueProfile::test_create_value_profile PASSED
tests/test_scoring.py::TestContentScorer::test_score_learning_content PASSED
...
======================= 20 passed in 0.42s =======================
```

---

## 🌐 Extension Development

### Browser Extension Adapter

Phaethon is designed to be integrated with browser extensions that intercept content and request evaluations.

**Example Flow:**

```javascript
// Browser extension content script
const content = {
  content_id: "page-" + Date.now(),
  source: document.location.href,
  title: document.title,
  content_type: "website",
  domain: new URL(document.location).hostname
};

// Request evaluation from Phaethon backend
fetch('http://localhost:8001/api/evaluate?user_id=user-1', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(content)
})
.then(r => r.json())
.then(decision => {
  if (decision.decision === 'BLOCK') {
    // Hide the page or show warning
    document.body.innerHTML = `<div class="phaethon-blocked">
      This content is misaligned with your values: ${decision.reasoning}
    </div>`;
  }
});
```

### HTTP/DNS Proxy Adapter

Implement a proxy that intercepts DNS/HTTP traffic and evaluates content before displaying.

### Custom Metric Scoring

Extend `ContentScorer` to add domain-specific scoring logic:

```python
class CustomScorer(ContentScorer):
    def _calculate_value_alignment(self, content, features, values):
        scores = super()._calculate_value_alignment(content, features, values)
        
        # Add custom logic
        if "research-paper" in content.domain:
            scores["academic_rigor"] = 0.95
        
        return scores
```

---

## 📊 Data Models

Key Pydantic models defined in [phaethon/core/schemas.py](phaethon/core/schemas.py):

- **ContentItem**: Piece of content to evaluate
- **UserProfile**: Complete user profile with values and rules  
- **ValueProfile**: Hierarchy of user values with confidence
- **ScoringResult**: Detailed scoring of content
- **InterventionDecision**: Final intervention decision
- **InterventionRule**: User-defined filtering rule
- **UserFeedback**: Feedback on a decision
- **EventLog**: Timestamped system event

---

## 🛠️ Development

### Project Structure

```
phaethon/
├── core/                    # Data models, user profiles, persistence
├── learning/               # Values inference, behavioral analysis
├── scoring/               # Content feature extraction & scoring
├── intervention/          # Rules engine, decision making
├── adapters/             # External system integrations (TODO)
├── server/               # FastAPI REST API
├── ui/                   # Web dashboard (planned)
├── tests/                # Comprehensive test suite
├── __main__.py           # Entry point
├── config.py             # Configuration
└── requirements.txt      # Dependencies
```

### Adding New Value Dimensions

1. Add to `config.py`:
```python
DEFAULT_VALUE_HIERARCHY = {
    "my_category": ["new_value_1", "new_value_2"]
}
```

2. Update scoring logic in `scoring/scorer.py`:
```python
if "new_value_1" in values.get("my_category", {}):
    new_value_alignment = 0.8  # Your logic
    scores["new_value_1"] = value * new_value_alignment
```

### Customizing Decision Logic

Override `DecisionEngine.make_decision()` or `_apply_safety_constraints()` to implement custom logic.

---

## 📈 Roadmap

### Phase 1 (Complete) ✅
- [x] Core data models and schemas
- [x] Values inference engine
- [x] Content scoring system
- [x] Intervention decision engine
- [x] Feedback processing
- [x] REST API skeleton
- [x] Unit tests

### Phase 2 (Next)
- [ ] Browser extension adapter
- [ ] Real-time content interception
- [ ] Web dashboard UI
- [ ] User feedback UI

### Phase 3 (Future)
- [ ] Advanced ML scoring (embeddings)
- [ ] Reinforcement learning for weighting
- [ ] Multi-adapter support
- [ ] A/B testing framework
- [ ] Analytics dashboard

---

## 📚 Further Reading

- [Architecture Documentation](./ARCHITECTURE.md)
- [API Specification](./API.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

## 📝 License

[Your License Here]

---

## 👥 Authors

Built during the Consciousness Hackathon 2026.

---

**Protect your attention. Align with your values. Use Phaethon.** 🔥
