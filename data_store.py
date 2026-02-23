"""
Data persistence module for storing user profiles and emotional history
Uses JSON files for simple, private local storage
Includes encryption for sensitive data when enabled
"""

import json
import os
from datetime import datetime
from pathlib import Path
import base64
import hashlib
from cryptography.fernet import Fernet
import config


class DataStore:
    """Manages persistent storage of user data with optional encryption"""
    
    def __init__(self, data_dir=None, encryption_key=None):
        """Initialize data store with directory path"""
        if data_dir is None:
            # Use user's home directory for privacy
            self.data_dir = Path.home() / '.wellness_buddy'
        else:
            self.data_dir = Path(data_dir)
        
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up encryption if enabled
        self.encryption_enabled = config.ENABLE_DATA_ENCRYPTION
        if self.encryption_enabled:
            self._setup_encryption(encryption_key)
        else:
            self.cipher = None
    
    def _setup_encryption(self, key=None):
        """Set up encryption with a key"""
        key_file = self.data_dir / '.encryption_key'
        
        if key:
            # Use provided key
            self.encryption_key = key
        elif key_file.exists():
            # Load existing key
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generate new key
            self.encryption_key = Fernet.generate_key()
            # Save key securely
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Restrict permissions to owner only
            os.chmod(key_file, 0o600)
        
        self.cipher = Fernet(self.encryption_key)
    
    def _encrypt_data(self, data):
        """Encrypt data before saving"""
        if not self.encryption_enabled or not self.cipher:
            return data
        
        json_data = json.dumps(data).encode()
        encrypted = self.cipher.encrypt(json_data)
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt data after loading"""
        if not self.encryption_enabled or not self.cipher:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return json.loads(decrypted.decode())
        except (base64.binascii.Error, json.JSONDecodeError) as e:
            # Likely legacy unencrypted data - return as is
            import logging
            logging.debug(f"Data appears to be unencrypted legacy format: {e}")
            return encrypted_data
        except Exception as e:
            # Genuine decryption error (wrong key, corrupted data, etc.)
            import logging
            logging.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt data. The encryption key may be incorrect or the data may be corrupted: {e}")
    
    def _get_user_file(self, user_id):
        """Get the file path for a user's data"""
        return self.data_dir / f"{user_id}.json"
    
    def save_user_data(self, user_id, data):
        """Save user profile and history data with optional encryption"""
        user_file = self._get_user_file(user_id)
        
        # Convert datetime objects to strings for JSON serialization
        serializable_data = self._prepare_for_serialization(data)
        
        if self.encryption_enabled and self.cipher:
            # Save encrypted data
            encrypted_data = self._encrypt_data(serializable_data)
            with open(user_file, 'w') as f:
                json.dump({'encrypted': True, 'data': encrypted_data}, f)
        else:
            # Save unencrypted data
            with open(user_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
        
        # Set file permissions to owner-only
        os.chmod(user_file, 0o600)
    
    def load_user_data(self, user_id):
        """Load user profile and history data with optional decryption"""
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            return None
        
        with open(user_file, 'r') as f:
            data = json.load(f)
        
        # Check if data is encrypted
        if isinstance(data, dict) and data.get('encrypted'):
            # Decrypt the data
            decrypted_data = self._decrypt_data(data['data'])
            return self._restore_from_serialization(decrypted_data)
        else:
            # Unencrypted legacy data
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
            datetime_fields = ['timestamp', 'created_at', 'last_session', 'added_at', 'marked_at', 
                             'last_activity', 'lockout_until']
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
    
    def create_backup(self, user_id):
        """Create a backup of user data"""
        user_file = self._get_user_file(user_id)
        if user_file.exists():
            backup_file = self.data_dir / f"{user_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import shutil
            shutil.copy2(user_file, backup_file)
            os.chmod(backup_file, 0o600)
            return backup_file
        return None
    
    def get_data_integrity_hash(self, user_id):
        """Calculate integrity hash for user data"""
        user_file = self._get_user_file(user_id)
        if not user_file.exists():
            return None
        
        with open(user_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
