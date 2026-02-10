"""Behavioral pattern discovery and analysis."""

import logging
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BehavioralAnalyzer:
    """Analyzes user behavioral patterns to identify trends and context."""
    
    def __init__(self):
        """Initialize behavioral analyzer."""
        self.patterns = defaultdict(list)
    
    def analyze_time_of_day_patterns(self, engagement_history: List[Dict]) -> Dict[str, float]:
        """Analyze engagement patterns by time of day.
        
        Args:
            engagement_history: List of engagement events with timestamps.
        
        Returns:
            Dict mapping hour (0-23) to average engagement score.
        """
        hourly_engagement = defaultdict(list)
        
        for event in engagement_history:
            if "timestamp" in event:
                hour = event["timestamp"].hour
                engagement_score = event.get("engagement_score", 0.5)
                hourly_engagement[hour].append(engagement_score)
        
        # Average by hour
        hourly_patterns = {}
        for hour in range(24):
            if hour in hourly_engagement:
                hourly_patterns[hour] = sum(hourly_engagement[hour]) / len(hourly_engagement[hour])
            else:
                hourly_patterns[hour] = 0.5
        
        logger.debug(f"Analyzed time-of-day patterns")
        return hourly_patterns
    
    def analyze_content_type_preferences(self, engagement_history: List[Dict]) -> Dict[str, float]:
        """Analyze preference patterns by content type.
        
        Args:
            engagement_history: List of engagement events.
        
        Returns:
            Dict mapping content type to average engagement score.
        """
        type_engagement = defaultdict(list)
        
        for event in engagement_history:
            content_type = event.get("content_type", "unknown")
            engagement_score = event.get("engagement_score", 0.5)
            type_engagement[content_type].append(engagement_score)
        
        # Average by content type
        type_patterns = {}
        for content_type, scores in type_engagement.items():
            type_patterns[content_type] = sum(scores) / len(scores)
        
        logger.debug(f"Analyzed content type preferences")
        return type_patterns
    
    def analyze_domain_preferences(self, engagement_history: List[Dict]) -> Dict[str, float]:
        """Analyze preference patterns by domain.
        
        Args:
            engagement_history: List of engagement events.
        
        Returns:
            Dict mapping domain to average engagement score.
        """
        domain_engagement = defaultdict(list)
        
        for event in engagement_history:
            domain = event.get("domain", "unknown")
            engagement_score = event.get("engagement_score", 0.5)
            domain_engagement[domain].append(engagement_score)
        
        # Average by domain, only include domains with enough data
        domain_patterns = {}
        for domain, scores in domain_engagement.items():
            if len(scores) >= 2:  # Need at least 2 events
                domain_patterns[domain] = sum(scores) / len(scores)
        
        logger.debug(f"Analyzed domain preferences for {len(domain_patterns)} domains")
        return domain_patterns
    
    def detect_attention_fragmentation(self, engagement_history: List[Dict],
                                      window_minutes: int = 60) -> float:
        """Detect if user is fragmenting attention across many items.
        
        Args:
            engagement_history: List of engagement events with timestamps.
            window_minutes: Time window for counting items.
        
        Returns:
            Fragmentation score (0-1, higher = more fragmented).
        """
        if not engagement_history:
            return 0.0
        
        # Count items in recent window
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        items_in_window = [
            e for e in engagement_history
            if e.get("timestamp", now) >= window_start
        ]
        
        # Fragmentation = high number of items with low dwell time
        avg_time_per_item = (
            sum(e.get("time_spent", 0) for e in items_in_window) / len(items_in_window)
            if items_in_window else 0
        )
        
        # Normalize: >30s per item = low fragmentation
        fragmentation_score = max(0.0, (30.0 - avg_time_per_item) / 30.0)
        fragmentation_score = min(1.0, fragmentation_score)
        
        logger.debug(f"Attention fragmentation score: {fragmentation_score:.2f}")
        return fragmentation_score
    
    def identify_distraction_triggers(self, engagement_history: List[Dict],
                                     goal_topics: Optional[List[str]] = None) -> List[Dict]:
        """Identify content that typically distracts from user goals.
        
        Args:
            engagement_history: List of engagement events.
            goal_topics: Optional list of goal-aligned topics.
        
        Returns:
            List of potential distraction triggers with scores.
        """
        distraction_triggers = []
        
        if not goal_topics:
            goal_topics = []
        
        # Identify content that wasn't about goals but consumed significant time
        off_topic_items = []
        for event in engagement_history:
            event_topics = event.get("topics", [])
            is_goal_related = any(
                topic.lower() in [t.lower() for t in goal_topics]
                for topic in event_topics
            )
            
            if not is_goal_related and event.get("time_spent", 0) > 120:  # >2 min off-topic
                off_topic_items.append(event)
        
        # Group by domain/type to find patterns
        domain_trigger_count = defaultdict(lambda: {"count": 0, "total_time": 0})
        for item in off_topic_items:
            domain = item.get("domain", "unknown")
            domain_trigger_count[domain]["count"] += 1
            domain_trigger_count[domain]["total_time"] += item.get("time_spent", 0)
        
        # Sort by frequency
        for domain, stats in sorted(domain_trigger_count.items(), 
                                   key=lambda x: x[1]["count"], reverse=True):
            if stats["count"] >= 2:  # Must occur multiple times to be a trigger
                distraction_triggers.append({
                    "domain": domain,
                    "trigger_strength": min(1.0, stats["count"] / 10),
                    "avg_time_wasted": stats["total_time"] / stats["count"],
                })
        
        logger.debug(f"Found {len(distraction_triggers)} distraction triggers")
        return distraction_triggers
    
    def estimate_user_state(self, recent_events: List[Dict], 
                           time_window_minutes: int = 30) -> Dict[str, float]:
        """Estimate current user state based on recent engagement.
        
        Args:
            recent_events: Recent engagement events.
            time_window_minutes: How far back to look.
        
        Returns:
            Dict with estimated state: {
                "focus_level": 0-1,
                "energy_level": 0-1,
                "stress_level": 0-1,
                "distraction_level": 0-1,
            }
        """
        if not recent_events:
            return {
                "focus_level": 0.5,
                "energy_level": 0.5,
                "stress_level": 0.5,
                "distraction_level": 0.5,
            }
        
        # Simple heuristics
        avg_dwell_time = sum(e.get("time_spent", 0) for e in recent_events) / len(recent_events)
        click_frequency = len(recent_events) / time_window_minutes
        
        # High dwell time = high focus
        focus_level = min(1.0, avg_dwell_time / 300)  # Normalize to 5 min
        
        # High click frequency = potential distraction
        distraction_level = min(1.0, click_frequency / 3.0)  # Normalize
        
        return {
            "focus_level": focus_level,
            "energy_level": 0.5,  # Can't estimate from these signals alone
            "stress_level": 0.5,
            "distraction_level": distraction_level,
        }
