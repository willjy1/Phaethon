# 🔥 Phaethon: Attention Firewall Architecture

A consciousness-aware attention firewall that learns users' higher-order productive values and curates their entire digital experience by intelligently filtering and prioritizing content.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Digital Surfaces                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │   Browser    │ │    HTTP/DNS  │ │  Application │             │
│  │  Extension   │ │    Proxy     │ │  APIs        │             │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Content       │
                    │   Interceptor   │
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌──────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Content    │    │    Values    │    │   Intervention  │
│   Processor  │    │   Inference  │    │   Engine        │
└──────┬───────┘    └──────┬───────┘    └────────┬────────┘
       │                   │                     │
       └───────────────────┼─────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Content   │
                    │   Scorer    │
                    └──────┬──────┘
                           │
                    ┌──────▼────────┐
                    │   Decision    │
                    │   Engine      │
                    └──────┬────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌────────┐        ┌────────┐       ┌────────┐
    │  Block │        │ Allow  │       │Priorit.│
    └────────┘        └────────┘       └────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼────────┐
                    │   Feedback    │
                    │   Loop        │
                    └──────┬────────┘
                           │
                    ┌──────▼──────┐
                    │   Learning  │
                    │   System    │
                    └─────────────┘
```

---

## Core Components

### 1. **Values Inference Engine**
Learns users' higher-order productive values from behavioral signals.

**Key Concepts:**
- **Explicit Values**: User-provided goals and principles
- **Inferred Values**: Learned from engagement patterns, attention allocation, explicit feedback
- **Hierarchical Values**: High-level principles decomposed into specific content preferences
- **Temporal Dynamics**: Value evolution over time

**Data Inputs:**
- Time-on-page / engagement duration
- Click patterns and interaction sequences
- Explicit user feedback (rating content, setting rules)
- User self-assessment (goal check-ins)
- Achievement of stated objectives

**Output:**
```python
{
    "values": {
        "productivity": {
            "focus": 0.92,      # How much user values deep work
            "learning": 0.87,   # Desire to acquire new knowledge
            "output_quality": 0.95,
        },
        "wellbeing": {
            "sleep_quality": 0.89,
            "stress_management": 0.76,
        }
    },
    "confidence": 0.78,  # Certainty in inferred values
    "updated_at": "2026-02-10T12:34:56Z"
}
```

### 2. **Content Scorer**
Evaluates content against learned values.

**Scoring Dimensions:**
- **Alignment Score** (0-1): How well content matches user values
- **Productivity Impact** (-)1 to +1): Expected effect on stated goals
- **Wellbeing Impact** (.0-1): Effect on user wellbeing
- **Confidence**: How certain the scoring is

**Scoring Algorithm:**
1. **Content Feature Extraction**: Title, description, domain, content type, metadata
2. **Semantic Analysis**: Main topics, tone, emotional valence
3. **Alignment Matching**: Compare extracted features against value profiles
4. **Historical Matching**: Similar content user previously rated
5. **Temporal Context**: Time of day, user current state

**Output:**
```python
{
    "content_id": "article-abc123",
    "title": "Deep Learning Paper Summary",
    "alignment_score": 0.91,  # Matches learning value
    "productivity_impact": 0.85,
    "wellbeing_impact": -0.12,  # Might be stressful
    "confidence": 0.87,
    "reasoning": "High-value learning content (matches learning value 0.87), likely increases focus (0.92)",
    "recommendation": "ALLOW_PRIORITIZE",
    "scores_by_value": {
        "focus": 0.85,
        "learning": 0.95,
        "productivity": 0.91
    }
}
```

### 3. **Intervention Engine**
Makes real-time filtering and prioritization decisions.

**Decision Types:**
- **BLOCK**: Prevent content from being shown (high misalignment + strong block rules)
- **ALLOW**: Let content through without modification
- **ALLOW_PRIORITIZE**: Show content but elevate it in feeds/search
- **ALLOW_MUTE**: Show content but reduce prominence (lower priority, greyed out)
- **ALLOW_WARNING**: Show content with a value-alignment warning
- **DEFER**: Queue for later (e.g., "Read this when you have deep focus time")

**Decision Logic:**
- Rule-based engine with user override capability
- Multi-factor weighting: alignment score + explicit rules + temporal context + user state
- Explainability: Provide reasoning for intervention

### 4. **Feedback Loop & Learning**
Continuous improvement through user interactions.

**Feedback Signals:**
- Explicit: User rates content after seeing decision
- Implicit: Click-through rates, time-on-content, return visits
- System: Achievement of stated goals, value drift detection
- Comparative: A/B testing different weighting strategies

**Learning Updates:**
- Real-time value refinement (Bayesian updates)
- Periodic values re-estimation (weekly/monthly)
- Behavioral pattern discovery (time-of-day effects, context sensitivity)
- Recommendation model fine-tuning

---

## Data Models

### Core Entities

**User Profile**
```python
{
    "user_id": "str",
    "created_at": "datetime",
    "updated_at": "datetime",
    "values": ValueProfile,
    "rules": List[InterventionRule],
    "preferences": UserPreferences,
    "settings": SystemSettings
}
```

**Content Item**
```python
{
    "content_id": "str",
    "source": "url | app_event | message",
    "title": "str",
    "content_type": "article | video | social | message | notification",
    "domain": "str",
    "metadata": {
        "author": "str",
        "timestamp": "datetime",
        "estimated_read_time": "int (seconds)",
        "topics": ["str"],
    },
    "extracted_features": ContentFeatures,
    "created_at": "datetime"
}
```

**Intervention Decision**
```python
{
    "decision_id": "str",
    "content_id": "str",
    "user_id": "str",
    "decision": "BLOCK | ALLOW | ALLOW_PRIORITIZE | ...",
    "scores": ScoringResult,
    "applied_rules": [{"rule_id": "str", "weight": 0.5}],
    "reasoning": "str",
    "timestamp": "datetime",
    "user_feedback": Optional[UserFeedback],
    "actual_user_action": "viewed | dismissed | ignored | spent_time | returned"
}
```

---

## Integration Points

### Browser Extension Adapter
**Responsibilities:**
- Intercept HTTP requests (content preview)
- Prevent DOM elements from rendering (blocks)
- Modify page layouts (deprioritization)
- Inject warning overlays
- Collect engagement metrics

**Protocol:**
```javascript
// Outbound (browser → service)
{
    type: "content.check",
    content: {
        url: "https://...",
        title: "...",
        timestamp: Date.now()
    }
}

// Inbound (service → browser)
{
    decision: "BLOCK",
    contentId: "...",
    reason: "Misaligned with focus values"
}
```

### HTTP/DNS Proxy Adapter
**Responsibilities:**
- Intercept DNS requests
- Block entire domains (hard blocks)
- Route traffic for logging/analysis
- Collect aggregate metrics

### Application API Adapter
**Responsibilities:**
- REST API for third-party app integration
- OAuth/token-based authentication
- Rate limiting and abuse prevention
- Webhook support for real-time events

---

## Algorithm Flow: Content Intervention

```
1. CONTENT_ARRIVAL
   └─> Extract features (title, domain, type, metadata)
   └─> Format as ContentItem

2. RETRIEVAL
   └─> Load user profile and values
   └─> Load explicit user intervention rules

3. SCORING
   └─> Feature extraction (semantic analysis)
   └─> Historical matching (similar content seen before)
   └─> Value alignment calculation
   └─> Productivity & wellbeing impact estimation
   └─> Confidence estimation
   └─> Generate ScoringResult

4. DECISION
   └─> Apply explicit user rules (whitelist/blacklist)
   └─> Check safety constraints
   └─> Weigh scores and rules
   └─> Determine intervention decision
   └─> Generate reasoning

5. ACTION
   └─> Execute intervention (block/allow/prioritize)
   └─> Log decision with reasoning
   └─> Return metadata to requesting adapter

6. FEEDBACK (post-interaction)
   └─> Collect user action signals
   └─> Update engagement metrics
   └─> If user provides explicit feedback:
       └─> Refine value estimates
       └─> Update historical patterns
```

---

## Technology Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API + WebSocket)
- Pydantic (data validation)
- SQLite/PostgreSQL (persistent storage)
- NumPy/Scikit-learn (ML scoring)

**Frontend/UI:**
- React (dashboard)
- Plotly (analytics visualization)
- WebSocket (real-time updates)

**Browser Extension:**
- Manifest V3 (Chrome/Edge)
- Content scripts
- Background service worker

**ML/Learning:**
- Bayesian inference (value updates)
- Similarity search (e.g., embedding-based content matching)
- Reinforcement learning (optional, for dynamic weighting)

---

## Initial MVP Scope

**Phase 1 (Foundation):**
- ✅ Data models and schemas
- ✅ Core values inference engine (Bayesian)
- ✅ Simple content scorer (rule + keyword-based)
- ✅ Intervention decision engine
- ✅ REST API skeleton
- ✅ SQLite persistence
- ✅ Basic UI (dashboard)

**Phase 2 (First Adapter):**
- Browser extension OR proxy adapter
- Real-time content interception
- Engagement metric collection

**Phase 3 (Learning):**
- Feedback loop implementation
- Value refinement algorithms
- Behavioral pattern analysis

**Phase 4 (Advanced):**
- Multiple adapters
- Advanced ML scoring (embeddings)
- Reinforcement learning
- A/B testing framework

---

## File Structure

```
phaethon/
├── core/                      # Core data models and business logic
│   ├── __init__.py
│   ├── schemas.py            # Pydantic models
│   ├── user_profile.py       # User state management
│   └── event_log.py          # Event tracking and persistence
│
├── learning/                  # Values inference engine
│   ├── __init__.py
│   ├── values_estimator.py   # Bayesian value inference
│   ├── behavioral_patterns.py # Pattern discovery
│   └── feedback_processor.py  # Feedback integration
│
├── scoring/                   # Content scoring system
│   ├── __init__.py
│   ├── content_features.py   # Feature extraction
│   ├── scorer.py             # Scoring engine
│   └── historical_matcher.py # Similar content matching
│
├── intervention/              # Decision & action engine
│   ├── __init__.py
│   ├── rules_engine.py       # User rules evaluation
│   ├── decision_engine.py    # Intervention decisions
│   └── actions.py            # Intervention actions
│
├── adapters/                  # External system adapters
│   ├── __init__.py
│   ├── base.py               # Abstract adapter
│   ├── browser_extension.py  # Browser ext interface
│   ├── proxy.py              # HTTP/DNS proxy
│   └── oauth_api.py          # Third-party API
│
├── server/                    # FastAPI backend
│   ├── __init__.py
│   ├── app.py                # Main app + endpoints
│   ├── websocket.py          # Real-time updates
│   └── middleware.py         # Auth, logging
│
├── ui/                        # Web dashboard
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── tests/                     # Test suite
│   ├── test_values_learning.py
│   ├── test_scoring.py
│   ├── test_decision_engine.py
│   └── test_integration.py
│
├── __init__.py
├── __main__.py
├── config.py
└── requirements.txt
```

