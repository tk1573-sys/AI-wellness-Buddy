"""
Data persistence module for storing user profiles and emotional history
Uses JSON files for simple, private local storage
"""

import json
import os
from datetime import datetime
from pathlib import Path


class DataStore:
    """Manages persistent storage of user data"""
    
    def __init__(self, data_dir=None):
        """Initialize data store with directory path"""
        if data_dir is None:
            # Use user's home directory for privacy
            self.data_dir = Path.home() / '.wellness_buddy'
        else:
            self.data_dir = Path(data_dir)
        
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_user_file(self, user_id):
        """Get the file path for a user's data"""
        return self.data_dir / f"{user_id}.json"
    
    def save_user_data(self, user_id, data):
        """Save user profile and history data"""
        user_file = self._get_user_file(user_id)
        
        # Convert datetime objects to strings for JSON serialization
        serializable_data = self._prepare_for_serialization(data)
        
        with open(user_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
    
    def load_user_data(self, user_id):
        """Load user profile and history data"""
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            return None
        
        with open(user_file, 'r') as f:
            data = json.load(f)
        
        return self._restore_from_serialization(data)
    
    def user_exists(self, user_id):
        """Check if a user profile exists"""
        return self._get_user_file(user_id).exists()
    
    def list_users(self):
        """List all user IDs with profiles"""
        users = []
        for file in self.data_dir.glob("*.json"):
            users.append(file.stem)
        return users
    
    def delete_user_data(self, user_id):
        """Delete a user's data (user control)"""
        user_file = self._get_user_file(user_id)
        if user_file.exists():
            user_file.unlink()
            return True
        return False
    
    def _prepare_for_serialization(self, data):
        """Convert datetime objects to ISO format strings"""
        if isinstance(data, dict):
            return {k: self._prepare_for_serialization(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_serialization(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
    
    def _restore_from_serialization(self, data):
        """Restore datetime objects from ISO format strings"""
        if isinstance(data, dict):
            # Check if this dict has datetime fields to restore
            result = {}
            datetime_fields = ['timestamp', 'created_at', 'last_session', 'added_at', 'marked_at']
            for k, v in data.items():
                if k in datetime_fields and isinstance(v, str):
                    try:
                        result[k] = datetime.fromisoformat(v)
                    except (ValueError, TypeError):
                        result[k] = v
                else:
                    result[k] = self._restore_from_serialization(v)
            return result
        elif isinstance(data, list):
            return [self._restore_from_serialization(item) for item in data]
        else:
            return data
