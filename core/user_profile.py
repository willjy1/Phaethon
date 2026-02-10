"""User profile management and persistence."""

import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .schemas import (
    UserProfile, 
    ValueProfile, 
    InterventionRule, 
    UserPreferences, 
    SystemSettings
)

logger = logging.getLogger(__name__)


class UserProfileManager:
    """Manages user profile persistence and retrieval."""
    
    def __init__(self, db_path: str = None):
        """Initialize user profile manager.
        
        Args:
            db_path: Path to SQLite database. Defaults to ./data/phaethon.db
        """
        if db_path is None:
            db_path = "./data/phaethon.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                values_json TEXT,
                rules_json TEXT,
                preferences_json TEXT,
                settings_json TEXT,
                total_content_processed INTEGER DEFAULT 0,
                total_decisions_made INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Event log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_logs (
                event_id TEXT PRIMARY KEY,
                user_id TEXT,
                level TEXT,
                code TEXT,
                message TEXT,
                metadata_json TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str) -> UserProfile:
        """Create a new user profile with default values."""
        profile = UserProfile(
            user_id=user_id,
            values=ValueProfile(values={}, confidence=0.0),
            rules=[],
            preferences=UserPreferences(),
            settings=SystemSettings(),
        )
        self.save_user(profile)
        logger.info(f"Created user profile: {user_id}")
        return profile
    
    def save_user(self, profile: UserProfile) -> None:
        """Save user profile to database."""
        profile.updated_at = datetime.utcnow()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, values_json, rules_json, preferences_json, settings_json, 
             total_content_processed, total_decisions_made, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.user_id,
            profile.values.model_dump_json(),
            json.dumps([r.model_dump() for r in profile.rules]),
            profile.preferences.model_dump_json(),
            profile.settings.model_dump_json(),
            profile.total_content_processed,
            profile.total_decisions_made,
            profile.created_at.isoformat(),
            profile.updated_at.isoformat(),
        ))
        
        conn.commit()
        conn.close()
        logger.debug(f"Saved user profile: {profile.user_id}")
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT values_json, rules_json, preferences_json, settings_json,
                   total_content_processed, total_decisions_made,
                   created_at, updated_at
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        values_json, rules_json, prefs_json, settings_json, processed, decisions, created, updated = row
        
        values = ValueProfile.model_validate_json(values_json)
        rules = [
            InterventionRule.model_validate(r) 
            for r in json.loads(rules_json)
        ]
        preferences = UserPreferences.model_validate_json(prefs_json)
        settings = SystemSettings.model_validate_json(settings_json)
        
        profile = UserProfile(
            user_id=user_id,
            values=values,
            rules=rules,
            preferences=preferences,
            settings=settings,
            total_content_processed=processed,
            total_decisions_made=decisions,
            created_at=datetime.fromisoformat(created),
            updated_at=datetime.fromisoformat(updated),
        )
        
        return profile
    
    def get_or_create_user(self, user_id: str) -> UserProfile:
        """Get user profile, creating if not found."""
        profile = self.get_user(user_id)
        if profile is None:
            profile = self.create_user(user_id)
        return profile
    
    def add_rule(self, user_id: str, rule: InterventionRule) -> None:
        """Add intervention rule to user profile."""
        profile = self.get_user(user_id)
        if profile is None:
            raise ValueError(f"User {user_id} not found")
        
        profile.rules.append(rule)
        self.save_user(profile)
        logger.info(f"Added rule {rule.rule_id} to user {user_id}")
    
    def remove_rule(self, user_id: str, rule_id: str) -> None:
        """Remove intervention rule from user profile."""
        profile = self.get_user(user_id)
        if profile is None:
            raise ValueError(f"User {user_id} not found")
        
        profile.rules = [r for r in profile.rules if r.rule_id != rule_id]
        self.save_user(profile)
        logger.info(f"Removed rule {rule_id} from user {user_id}")
    
    def update_values(self, user_id: str, values: ValueProfile) -> None:
        """Update user values."""
        profile = self.get_user(user_id)
        if profile is None:
            raise ValueError(f"User {user_id} not found")
        
        profile.values = values
        self.save_user(profile)
        logger.info(f"Updated values for user {user_id}")
    
    def update_preferences(self, user_id: str, preferences: UserPreferences) -> None:
        """Update user preferences."""
        profile = self.get_user(user_id)
        if profile is None:
            raise ValueError(f"User {user_id} not found")
        
        profile.preferences = preferences
        self.save_user(profile)
        logger.info(f"Updated preferences for user {user_id}")
    
    def update_statistics(self, user_id: str, content_processed: int = 1, decisions_made: int = 1) -> None:
        """Update user statistics."""
        profile = self.get_user(user_id)
        if profile is None:
            raise ValueError(f"User {user_id} not found")
        
        profile.total_content_processed += content_processed
        profile.total_decisions_made += decisions_made
        self.save_user(profile)


class EventLogger:
    """Manages event logging."""
    
    def __init__(self, db_path: str = None):
        """Initialize event logger.
        
        Args:
            db_path: Path to SQLite database.
        """
        if db_path is None:
            db_path = "./data/phaethon.db"
        
        self.db_path = Path(db_path)
    
    def log_event(self, event_id: str, user_id: Optional[str], level: str, 
                  code: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log an event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO event_logs (event_id, user_id, level, code, message, metadata_json, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            user_id,
            level,
            code,
            message,
            json.dumps(metadata or {}),
            datetime.utcnow().isoformat(),
        ))
        
        conn.commit()
        conn.close()
        logger.debug(f"Logged event {code}: {message}")
    
    def get_events(self, user_id: Optional[str] = None, level: Optional[str] = None, 
                   limit: int = 100) -> list:
        """Retrieve events from log."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM event_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return rows
