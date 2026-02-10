"""Phaethon global configuration."""

from pathlib import Path
from typing import Dict, List

# Data paths
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "phaethon.db"
VALUES_DIR = DATA_DIR / "values"
VALUES_DIR.mkdir(exist_ok=True)

# Default value hierarchy
DEFAULT_VALUE_HIERARCHY: Dict[str, List[str]] = {
    "productivity": [
        "focus",
        "learning",
        "output_quality",
        "efficiency",
    ],
    "wellbeing": [
        "sleep_quality",
        "stress_management",
        "mood",
        "physical_health",
    ],
    "relationships": [
        "family_time",
        "friend_connection",
        "community",
    ],
    "personal_growth": [
        "creativity",
        "skill_development",
        "self_reflection",
    ],
}

# Scoring thresholds
ALIGNMENT_SCORE_THRESHOLD = 0.6  # Below this = consider blocking
PRODUCTIVITY_IMPACT_THRESHOLD = -0.3  # Negative impact on productivity
WELLBEING_IMPACT_THRESHOLD = -0.3  # Negative impact on wellbeing

# Update thresholds
MIN_FEEDBACK_FOR_VALUE_UPDATE = 10
DAYS_BETWEEN_VALUE_UPDATES = 7

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Frontend
API_HOST = "0.0.0.0"
API_PORT = 8001  # Different from STV testbed port 8000
API_WORKERS = 4

# Feature flags
ENABLE_LEARNING = True
ENABLE_INTERVENTION = True
ENABLE_FEEDBACK_COLLECTION = True
