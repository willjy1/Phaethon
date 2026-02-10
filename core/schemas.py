"""Phaethon Pydantic data models for core entities."""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ContentType(str, Enum):
    """Content source types."""
    ARTICLE = "article"
    VIDEO = "video"
    SOCIAL_POST = "social_post"
    MESSAGE = "message"
    NOTIFICATION = "notification"
    EMAIL = "email"
    WEBSITE = "website"
    UNKNOWN = "unknown"


class InterventionAction(str, Enum):
    """Possible intervention actions."""
    BLOCK = "BLOCK"
    ALLOW = "ALLOW"
    ALLOW_PRIORITIZE = "ALLOW_PRIORITIZE"
    ALLOW_MUTE = "ALLOW_MUTE"
    ALLOW_WARNING = "ALLOW_WARNING"
    DEFER = "DEFER"


class FeedbackType(str, Enum):
    """Type of user feedback."""
    EXPLICIT_RATING = "explicit_rating"
    ENGAGEMENT = "engagement"
    SYSTEM = "system"
    COMPARATIVE = "comparative"


class EventLevel(str, Enum):
    """Event severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# ============================================================================
# Content Models
# ============================================================================

class ContentMetadata(BaseModel):
    """Metadata about content."""
    model_config = ConfigDict(extra="allow")
    
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    estimated_read_time_seconds: Optional[int] = None
    topics: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    language: str = "en"


class ContentFeatures(BaseModel):
    """Extracted features from content."""
    model_config = ConfigDict(extra="allow")
    
    title: str
    summary: Optional[str] = None
    main_topics: List[str] = Field(default_factory=list)
    tone: Optional[str] = None  # "informative", "sensational", "educational", etc
    emotional_valence: Optional[float] = None  # -1 (negative) to +1 (positive)
    is_promotional: bool = False
    is_clickbait: bool = False
    domain_reputation: Optional[float] = None  # 0-1 scale


class ContentItem(BaseModel):
    """A piece of content to be evaluated."""
    
    content_id: str
    source: str  # URL, app event ID, message ID
    title: str
    content_type: ContentType
    domain: str
    
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)
    extracted_features: Optional[ContentFeatures] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Values and Preferences Models
# ============================================================================

class ValueDimension(BaseModel):
    """A single value dimension (e.g., "focus", "learning")."""
    name: str
    importance: float = Field(ge=0.0, le=1.0, default=0.5)
    description: Optional[str] = None


class ValueProfile(BaseModel):
    """User's value profile."""
    
    values: Dict[str, Dict[str, float]] = Field(
        description="Hierarchical values structure. E.g., {'productivity': {'focus': 0.92, 'learning': 0.87}}"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Certainty in inferred values")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPreferences(BaseModel):
    """User system preferences."""
    model_config = ConfigDict(extra="allow")
    
    max_update_frequency: int = Field(default=100, description="Max ms between updates")
    enable_explicit_feedback: bool = True
    enable_implicit_feedback: bool = True
    allow_value_inference: bool = True
    notification_level: str = "normal"  # "minimal", "normal", "verbose"


class SystemSettings(BaseModel):
    """System-wide settings."""
    model_config = ConfigDict(extra="allow")
    
    learning_enabled: bool = True
    intervention_enabled: bool = True
    logging_level: str = "INFO"
    data_retention_days: int = 365


class InterventionRule(BaseModel):
    """A user-defined intervention rule."""
    
    rule_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Rule conditions
    domain: Optional[str] = None  # Match specific domain
    content_type: Optional[ContentType] = None
    keyword_includes: List[str] = Field(default_factory=list)
    keyword_excludes: List[str] = Field(default_factory=list)
    
    # Rule action
    action: InterventionAction
    reason: str
    priority: int = Field(default=0, description="Higher = higher priority (0-100)")
    
    is_active: bool = True


class UserProfile(BaseModel):
    """Complete user profile."""
    
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Core preferences
    values: ValueProfile = Field(default_factory=lambda: ValueProfile(values={}, confidence=0.0))
    rules: List[InterventionRule] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    settings: SystemSettings = Field(default_factory=SystemSettings)
    
    # Engagement history (summary)
    total_content_processed: int = 0
    total_decisions_made: int = 0


# ============================================================================
# Scoring and Decision Models
# ============================================================================

class ScoringResult(BaseModel):
    """Result of content scoring against user values."""
    
    content_id: str
    user_id: str
    
    alignment_score: float = Field(ge=0.0, le=1.0, description="Overall alignment with values")
    productivity_impact: float = Field(ge=-1.0, le=1.0, description="Expected productivity effect")
    wellbeing_impact: float = Field(ge=-1.0, le=1.0, description="Expected wellbeing effect")
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Detailed breakdown
    scores_by_value: Dict[str, float] = Field(
        default_factory=dict, 
        description="Alignment score for each value dimension"
    )
    
    reasoning: str = Field(description="Human-readable explanation of score")
    recommended_action: InterventionAction
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserFeedback(BaseModel):
    """User feedback on an intervention decision."""
    
    decision_id: str
    user_id: str
    
    feedback_type: FeedbackType
    action_taken: Optional[str] = None  # "viewed", "dismissed", "ignored", "spent_time", "returned"
    
    # Explicit feedback
    rating: Optional[int] = Field(None, ge=-1, le=1)  # -1 (too strict), 0 (neutral), +1 (too lenient)
    comment: Optional[str] = None
    
    # Engagement metrics
    time_spent_seconds: Optional[float] = None
    interaction_count: Optional[int] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterventionDecision(BaseModel):
    """Result of intervention decision-making."""
    
    decision_id: str
    content_id: str
    user_id: str
    
    decision: InterventionAction
    scores: ScoringResult
    
    # Decision reasoning
    applied_rules: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Rules that influenced this decision"
    )
    reasoning: str
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Follow-up
    user_feedback: Optional[UserFeedback] = None


# ============================================================================
# Event and Logging Models
# ============================================================================

class EventLog(BaseModel):
    """Event log entry."""
    
    event_id: str
    user_id: Optional[str] = None
    
    level: EventLevel
    code: str  # e.g., "CONTENT_SCORED", "DECISION_MADE", "VALUE_UPDATED"
    message: str
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# API Request/Response Models
# ============================================================================

class EvaluateContentRequest(BaseModel):
    """Request to evaluate content."""
    
    content_id: str
    source: str
    title: str
    content_type: ContentType
    domain: str
    metadata: Optional[ContentMetadata] = None


class EvaluateContentResponse(BaseModel):
    """Response for content evaluation."""
    
    content_id: str
    decision: InterventionAction
    scoring: ScoringResult
    reasoning: str


class UpdateValuesRequest(BaseModel):
    """Request to update user values."""
    
    values: Dict[str, Dict[str, float]]
    confidence: Optional[float] = None
    force_update: bool = False


class GetUserProfileResponse(BaseModel):
    """Response for user profile retrieval."""
    
    user_id: str
    values: ValueProfile
    rules: List[InterventionRule]
    preferences: UserPreferences
    stats: Dict[str, Any]
