"""Phaethon main package initialization."""

from .core.schemas import (
    ContentItem,
    UserProfile,
    InterventionDecision,
    ScoringResult,
)
from .core.user_profile import UserProfileManager, EventLogger
from .learning.values_estimator import BayesianValuesEstimator
from .learning.behavioral_patterns import BehavioralAnalyzer
from .learning.feedback_processor import FeedbackProcessor
from .scoring.scorer import ContentScorer
from .intervention.decision_engine import DecisionEngine
from .intervention.rules_engine import RulesEngine

__version__ = "0.1.0"

__all__ = [
    "ContentItem",
    "UserProfile",
    "InterventionDecision",
    "ScoringResult",
    "UserProfileManager",
    "EventLogger",
    "BayesianValuesEstimator",
    "BehavioralAnalyzer",
    "FeedbackProcessor",
    "ContentScorer",
    "DecisionEngine",
    "RulesEngine",
]
