"""Phaethon FastAPI server and REST endpoints."""

import logging
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from datetime import datetime

from phaethon.core.schemas import (
    ContentItem,
    EvaluateContentRequest,
    EvaluateContentResponse,
    UpdateValuesRequest,
    GetUserProfileResponse,
    InterventionAction,
)
from phaethon.core.user_profile import UserProfileManager, EventLogger
from phaethon.learning.values_estimator import BayesianValuesEstimator
from phaethon.learning.feedback_processor import FeedbackProcessor
from phaethon.scoring.scorer import ContentScorer
from phaethon.intervention.decision_engine import DecisionEngine
from phaethon import config as config_module

# Setup logging
logging.basicConfig(
    level=getattr(logging, config_module.LOG_LEVEL),
    format=config_module.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Phaethon",
    description="Attention Firewall - Learning your values, protecting your focus",
    version="0.1.0",
)

# Initialize components
profile_manager = UserProfileManager(str(config_module.DB_PATH))
event_logger = EventLogger(str(config_module.DB_PATH))
values_estimator = BayesianValuesEstimator(str(config_module.VALUES_DIR))
feedback_processor = FeedbackProcessor()
content_scorer = ContentScorer()
decision_engine = DecisionEngine()


# ============================================================================
# Dependency Injection
# ============================================================================

def get_user_id(user_id: str = "default_user") -> str:
    """Get user ID from request headers or default."""
    return user_id


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@app.get("/api/status")
async def get_status(user_id: str = Depends(get_user_id)):
    """Get system status."""
    profile = profile_manager.get_or_create_user(user_id)
    
    return {
        "user_id": user_id,
        "values_confidence": profile.values.confidence,
        "active_rules_count": len([r for r in profile.rules if r.is_active]),
        "total_content_processed": profile.total_content_processed,
        "total_decisions_made": profile.total_decisions_made,
        "learning_enabled": config_module.ENABLE_LEARNING,
        "intervention_enabled": config_module.ENABLE_INTERVENTION,
    }


# ============================================================================
# Content Evaluation Endpoints
# ============================================================================

@app.post("/api/evaluate", response_model=EvaluateContentResponse)
async def evaluate_content(request: EvaluateContentRequest, user_id: str = Depends(get_user_id)):
    """Evaluate content and get intervention decision.
    
    This is the main endpoint for content evaluation. Returns a decision
    (BLOCK, ALLOW, ALLOW_PRIORITIZE, etc.) with reasoning.
    """
    # Get user profile
    user_profile = profile_manager.get_or_create_user(user_id)
    
    # Create content item
    content = ContentItem(
        content_id=request.content_id,
        source=request.source,
        title=request.title,
        content_type=request.content_type,
        domain=request.domain,
        metadata=request.metadata or {},
    )
    
    # Score content
    scoring_result = content_scorer.score_content(content, user_profile)
    
    # Make intervention decision
    decision = decision_engine.make_decision(content, user_profile, scoring_result)
    
    # Log decision
    event_logger.log_event(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        level="INFO",
        code="DECISION_MADE",
        message=f"Decision: {decision.decision.value}",
        metadata={
            "content_id": content.content_id,
            "decision": decision.decision.value,
            "alignment_score": scoring_result.alignment_score,
        }
    )
    
    # Update statistics
    profile_manager.update_statistics(user_id, content_processed=1, decisions_made=1)
    
    return EvaluateContentResponse(
        content_id=content.content_id,
        decision=decision.decision,
        scoring=scoring_result,
        reasoning=decision.reasoning,
    )


# ============================================================================
# User Profile Endpoints
# ============================================================================

@app.get("/api/profile", response_model=GetUserProfileResponse)
async def get_user_profile(user_id: str = Depends(get_user_id)):
    """Get user profile."""
    profile = profile_manager.get_or_create_user(user_id)
    
    return GetUserProfileResponse(
        user_id=profile.user_id,
        values=profile.values,
        rules=profile.rules,
        preferences=profile.preferences,
        stats={
            "total_content_processed": profile.total_content_processed,
            "total_decisions_made": profile.total_decisions_made,
            "active_rules": len([r for r in profile.rules if r.is_active]),
        }
    )


@app.post("/api/values/initialize")
async def initialize_values(user_id: str = Depends(get_user_id)):
    """Initialize user values with default hierarchy."""
    # Initialize values with default hierarchy
    values = values_estimator.initialize_values(config_module.DEFAULT_VALUE_HIERARCHY)
    
    # Get profile and update
    profile = profile_manager.get_or_create_user(user_id)
    profile_manager.update_values(user_id, values)
    
    event_logger.log_event(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        level="INFO",
        code="VALUES_INITIALIZED",
        message="User values initialized with default hierarchy",
    )
    
    return {"success": True, "values": values.model_dump()}


@app.post("/api/values/update")
async def update_values(request: UpdateValuesRequest, user_id: str = Depends(get_user_id)):
    """Manually update user values."""
    from phaethon.core.schemas import ValueProfile
    
    # Create new value profile
    new_values = ValueProfile(
        values=request.values,
        confidence=request.confidence or 0.7,
    )
    
    # Update profile
    profile_manager.update_values(user_id, new_values)
    
    event_logger.log_event(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        level="INFO",
        code="VALUES_UPDATED",
        message="User values manually updated",
        metadata={"force": request.force_update}
    )
    
    return {"success": True, "values": new_values.model_dump()}


# ============================================================================
# Rules Management Endpoints
# ============================================================================

@app.post("/api/rules")
async def create_rule(rule_data: dict, user_id: str = Depends(get_user_id)):
    """Create a new intervention rule."""
    from phaethon.core.schemas import InterventionRule
    
    # Generate rule ID
    rule_id = str(uuid.uuid4())
    
    # Create rule object
    rule = InterventionRule(
        rule_id=rule_id,
        **rule_data
    )
    
    # Validate rule
    is_valid, error = decision_engine.rules_engine.validate_rule(rule)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Add to profile
    profile_manager.add_rule(user_id, rule)
    
    event_logger.log_event(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        level="INFO",
        code="RULE_CREATED",
        message=f"Rule created: {rule.reason}",
        metadata={"rule_id": rule.rule_id}
    )
    
    return {"success": True, "rule_id": rule.rule_id}


@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: str, user_id: str = Depends(get_user_id)):
    """Delete an intervention rule."""
    profile_manager.remove_rule(user_id, rule_id)
    
    event_logger.log_event(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        level="INFO",
        code="RULE_DELETED",
        message=f"Rule deleted: {rule_id}",
    )
    
    return {"success": True}


# ============================================================================
# Feedback Endpoints
# ============================================================================

@app.post("/api/feedback")
async def submit_feedback(feedback_data: dict, user_id: str = Depends(get_user_id)):
    """Submit feedback on a decision."""
    from phaethon.core.schemas import UserFeedback
    
    # Create feedback object
    feedback = UserFeedback(
        user_id=user_id,
        **feedback_data
    )
    
    # Process feedback
    signal, confidence = feedback_processor.process_explicit_feedback(feedback)
    
    # Update values if enough feedback
    profile = profile_manager.get_user(user_id)
    if profile:
        updated_values = values_estimator.update_from_feedback(
            profile.values,
            feedback,
            config_module.DEFAULT_VALUE_HIERARCHY
        )
        if config_module.ENABLE_LEARNING:
            profile_manager.update_values(user_id, updated_values)
    
    event_logger.log_event(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        level="INFO",
        code="FEEDBACK_RECEIVED",
        message=f"Feedback received: {signal}",
        metadata={
            "signal": signal,
            "confidence": confidence,
            "rating": feedback.rating,
        }
    )
    
    return {
        "success": True,
        "signal": signal,
        "confidence": confidence,
    }


# ============================================================================
# Analytics & Insights Endpoints
# ============================================================================

@app.get("/api/analytics/value-trends")
async def get_value_trends(user_id: str = Depends(get_user_id), days: int = 30):
    """Get value evolution trends over time."""
    trends = values_estimator.estimate_value_evolution(user_id, days=days)
    
    return {
        "user_id": user_id,
        "period_days": days,
        "trends": trends,
    }


@app.get("/api/analytics/decision-stats")
async def get_decision_stats(user_id: str = Depends(get_user_id)):
    """Get statistics about decisions made."""
    profile = profile_manager.get_user(user_id)
    
    return {
        "user_id": user_id,
        "total_decisions": profile.total_decisions_made if profile else 0,
        "total_content_processed": profile.total_content_processed if profile else 0,
        "active_rules": len(profile.rules) if profile else 0,
    }


# ============================================================================
# Events & Logging Endpoints
# ============================================================================

@app.get("/api/events")
async def get_events(user_id: str = Depends(get_user_id), level: str = None, limit: int = 100):
    """Get event log entries."""
    events = event_logger.get_events(user_id=user_id, level=level, limit=limit)
    
    return {
        "user_id": user_id,
        "events": [
            {
                "event_id": e[0],
                "level": e[2],
                "code": e[3],
                "message": e[4],
                "timestamp": e[6],
            }
            for e in events
        ]
    }


# ============================================================================
# Static Files & UI
# ============================================================================

# Mount UI static files if they exist
ui_path = Path(__file__).parent / "ui"
if ui_path.exists():
    app.mount("/static", StaticFiles(directory=ui_path), name="static")


@app.get("/")
async def serve_ui():
    """Serve UI index."""
    ui_index = Path(__file__).parent / "ui" / "index.html"
    if ui_index.exists():
        return FileResponse(ui_index)
    return {"message": "Phaethon API running. UI not configured yet."}


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config_module.API_HOST,
        port=config_module.API_PORT,
        workers=config_module.API_WORKERS,
    )
