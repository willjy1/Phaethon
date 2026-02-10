# Phaethon API Quick Reference

## Getting Started

### 1. Start the Server
```bash
python -m phaethon
# Server running on http://localhost:8001
```

### 2. Initialize a User
```bash
curl -X POST http://localhost:8001/api/values/initialize?user_id=user-1
```

### 3. Set User's Values
```bash
curl -X POST http://localhost:8001/api/values/update?user_id=user-1 \
  -H "Content-Type: application/json" \
  -d '{
    "values": {
      "productivity": {
        "focus": 0.95,
        "learning": 0.87,
        "output_quality": 0.92
      },
      "wellbeing": {
        "sleep_quality": 0.89,
        "stress_management": 0.76
      }
    },
    "confidence": 0.85
  }'
```

## Core Workflow

### Evaluate Content

**Request:**
```bash
curl -X POST "http://localhost:8001/api/evaluate?user_id=user-1" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "article-tech-001",
    "source": "https://medium.com/@author/deep-learning-guide",
    "title": "Complete Guide to Deep Learning and Neural Networks",
    "content_type": "article",
    "domain": "medium.com"
  }'
```

**Response:**
```json
{
  "content_id": "article-tech-001",
  "decision": "ALLOW_PRIORITIZE",
  "scoring": {
    "alignment_score": 0.91,
    "productivity_impact": 0.85,
    "wellbeing_impact": 0.1,
    "confidence": 0.87,
    "scores_by_value": {
      "learning": 0.95,
      "focus": 0.85,
      "output_quality": 0.91
    },
    "reasoning": "High-quality learning content matching learning value 0.87; likely increases productivity (85%)"
  },
  "reasoning": "User rule matched content: ..."
}
```

**Decision Types:**
- `BLOCK` - Don't show content
- `ALLOW` - Show normally
- `ALLOW_PRIORITIZE` - Show at top of feed
- `ALLOW_MUTE` - Show but greyed out
- `ALLOW_WARNING` - Show with warning overlay
- `DEFER` - Queue for later viewing

---

## User Rules (Content Filtering)

### Create a Rule - Block All Twitter

```bash
curl -X POST "http://localhost:8001/api/rules?user_id=user-1" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "twitter.com",
    "action": "BLOCK",
    "reason": "Too distracting, procrastination trigger",
    "priority": 100
  }'
```

### Create a Rule - Prioritize Learning Content

```bash
curl -X POST "http://localhost:8001/api/rules?user_id=user-1" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_includes": ["tutorial", "guide", "how to", "learn"],
    "action": "ALLOW_PRIORITIZE",
    "reason": "Learning-focused content aligns with my goals",
    "priority": 80
  }'
```

### Create a Rule - Warn About News

```bash
curl -X POST "http://localhost:8001/api/rules?user_id=user-1" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "news.com",
    "action": "ALLOW_WARNING",
    "reason": "News can be stressful, show warning",
    "priority": 50
  }'
```

### Delete a Rule

```bash
curl -X DELETE "http://localhost:8001/api/rules/rule-id?user_id=user-1"
```

---

## Feedback (Improve Learning)

### Submit Explicit Rating

```bash
curl -X POST "http://localhost:8001/api/feedback?user_id=user-1" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "decision-1",
    "feedback_type": "explicit_rating",
    "rating": 1,
    "comment": "Actually I wanted to see that article, you were too strict"
  }'
```

**Rating Values:**
- `1`: "You were too strict" (blocked content I wanted)
- `0`: "Decision was neutral/okay"
- `-1`: "You were too lenient" (allowed content I didn't want)

### Submit Engagement Feedback

```bash
curl -X POST "http://localhost:8001/api/feedback?user_id=user-1" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "decision-1",
    "feedback_type": "engagement",
    "action_taken": "spent_time",
    "time_spent_seconds": 600
  }'
```

**Action Types:**
- `viewed`: Just saw it
- `dismissed`: Quickly closed
- `ignored`: Didn't interact
- `spent_time`: Spent significant time
- `returned`: Came back multiple times

---

## Analytics

### Get Profile Statistics

```bash
curl "http://localhost:8001/api/profile?user_id=user-1"
```

Response:
```json
{
  "user_id": "user-1",
  "values": {
    "values": {
      "productivity": {
        "focus": 0.93,
        "learning": 0.85
      }
    },
    "confidence": 0.78
  },
  "rules": [
    {
      "rule_id": "rule-1",
      "domain": "twitter.com",
      "action": "BLOCK",
      ...
    }
  ],
  "stats": {
    "total_content_processed": 42,
    "total_decisions_made": 42,
    "active_rules": 3
  }
}
```

### Get Decision Statistics

```bash
curl "http://localhost:8001/api/analytics/decision-stats?user_id=user-1"
```

### Get Event Log

```bash
curl "http://localhost:8001/api/events?user_id=user-1&level=INFO&limit=50"
```

### Get Value Evolution

```bash
curl "http://localhost:8001/api/analytics/value-trends?user_id=user-1&days=30"
```

---

## Content Type Reference

```
"article"         - Blog post, news article, research paper
"video"           - YouTube, Vimeo, etc.
"social_post"     - Tweet, Facebook post, Instagram
"message"         - Email, chat message
"notification"    - System notification, alert
"email"           - Email newsletter
"website"         - General website
"unknown"         - Unclassified
```

---

## Example Scenarios

### Scenario 1: Learning-Focused Developer

**Setup:**
```bash
# Initialize and set values
curl -X POST http://localhost:8001/api/values/initialize?user_id=dev-1

curl -X POST "http://localhost:8001/api/values/update?user_id=dev-1" \
  -d '{
    "values": {
      "productivity": {"focus": 0.95, "learning": 0.92},
      "wellbeing": {"sleep_quality": 0.88}
    }
  }'

# Create rules
curl -X POST "http://localhost:8001/api/rules?user_id=dev-1" \
  -d '{
    "domain": "twitter.com",
    "action": "BLOCK",
    "reason": "Procrastination",
    "priority": 100
  }'
```

**Testing:**
```bash
# Tech article → ALLOW_PRIORITIZE
curl -X POST "http://localhost:8001/api/evaluate?user_id=dev-1" \
  -d '{
    "content_id": "paper-1",
    "source": "https://arxiv.org/paper",
    "title": "Distributed Systems Paper",
    "content_type": "article",
    "domain": "arxiv.org"
  }'

# Social media → BLOCK (rule match)
curl -X POST "http://localhost:8001/api/evaluate?user_id=dev-1" \
  -d '{
    "content_id": "tweet-1",
    "source": "https://twitter.com/post",
    "title": "Random joke",
    "content_type": "social_post",
    "domain": "twitter.com"
  }'
```

### Scenario 2: Mindfulness Practitioner

**Setup:**
```bash
curl -X POST http://localhost:8001/api/values/initialize?user_id=mindful-1

curl -X POST "http://localhost:8001/api/values/update?user_id=mindful-1" \
  -d '{
    "values": {
      "wellbeing": {"stress_management": 0.95, "sleep_quality": 0.92}
    }
  }'

# Block stressful news
curl -X POST "http://localhost:8001/api/rules?user_id=mindful-1" \
  -d '{
    "keyword_includes": ["crisis", "death", "attack"],
    "action": "BLOCK",
    "reason": "Stressful content",
    "priority": 90
  }'
```

---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Not found
- `500` - Server error

### Example Error Response
```json
{
  "error": "Internal server error",
  "detail": "User not found"
}
```

---

## Best Practices

1. **Initialize User First**
   - Always run `POST /api/values/initialize` before evaluating content

2. **Set Clear Values**
   - Use specific, measurable value dimensions (0-1 scale)
   - Set confidence based on how sure you are

3. **Create Focused Rules**
   - One rule per concern (don't mix multiple domains in one rule)
   - Set appropriate priority (100 = must apply, 0 = optional)

4. **Provide Feedback**
   - Rate decisions to improve learning
   - Engage with content recommendations
   - System improves with every interaction

5. **Monitor Trends**
   - Check analytics regularly
   - Watch for value drift
   - Adjust rules as goals change

---

## Troubleshooting

**Q: Content scored but decision doesn't match expected outcome?**
A: Check your current values and rules with `GET /api/profile`. Rules always override scores.

**Q: System isn't learning from my feedback?**
A: Need 10+ feedback signals before values update. Check with `GET /api/events` for learning logs.

**Q: Want to reset a user?**
A: Delete the database at `./data/phaethon.db` and reinitialize.

---

## Integration Example (Python)

```python
import requests

BASE_URL = "http://localhost:8001"
USER_ID = "user-1"

# Initialize
requests.post(f"{BASE_URL}/api/values/initialize", params={"user_id": USER_ID})

# Evaluate content
response = requests.post(
    f"{BASE_URL}/api/evaluate",
    params={"user_id": USER_ID},
    json={
        "content_id": "article-1",
        "source": "https://example.com/article",
        "title": "Article Title",
        "content_type": "article",
        "domain": "example.com"
    }
)

decision = response.json()
print(f"Decision: {decision['decision']}")
print(f"Alignment: {decision['scoring']['alignment_score']:.0%}")

# Submit feedback
requests.post(
    f"{BASE_URL}/api/feedback",
    params={"user_id": USER_ID},
    json={
        "decision_id": "decision-1",
        "feedback_type": "explicit_rating",
        "rating": 1,
        "comment": "Too strict"
    }
)
```

---

For detailed documentation, see [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
