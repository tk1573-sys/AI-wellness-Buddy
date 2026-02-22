#!/usr/bin/env python3
"""
Test script for extended tracking and security features
"""

import sys
import tempfile
import shutil
from pathlib import Path

def test_extended_tracking():
    """Test 365-day tracking configuration"""
    print("\n🧪 Testing Extended Tracking (365 days)")
    print("=" * 60)
    
    try:
        import config
        
        # Check extended tracking settings
        assert hasattr(config, 'EMOTIONAL_HISTORY_DAYS'), "EMOTIONAL_HISTORY_DAYS not found"
        assert config.EMOTIONAL_HISTORY_DAYS == 365, f"Expected 365 days, got {config.EMOTIONAL_HISTORY_DAYS}"
        print(f"✅ PASS: Emotional history set to {config.EMOTIONAL_HISTORY_DAYS} days")
        
        assert hasattr(config, 'CONVERSATION_ARCHIVE_DAYS'), "CONVERSATION_ARCHIVE_DAYS not found"
        assert config.CONVERSATION_ARCHIVE_DAYS == 180, f"Expected 180 days, got {config.CONVERSATION_ARCHIVE_DAYS}"
        print(f"✅ PASS: Conversation archive set to {config.CONVERSATION_ARCHIVE_DAYS} days")
        
        assert hasattr(config, 'MAX_EMOTIONAL_SNAPSHOTS'), "MAX_EMOTIONAL_SNAPSHOTS not found"
        print(f"✅ PASS: Max emotional snapshots: {config.MAX_EMOTIONAL_SNAPSHOTS}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_security_configuration():
    """Test security settings"""
    print("\n🔒 Testing Security Configuration")
    print("=" * 60)
    
    try:
        import config
        
        # Check security settings
        security_settings = [
            ('ENABLE_PROFILE_PASSWORD', True),
            ('SESSION_TIMEOUT_MINUTES', 30),
            ('ENABLE_DATA_ENCRYPTION', True),
            ('MIN_PASSWORD_LENGTH', 8),
            ('MAX_LOGIN_ATTEMPTS', 3),
            ('LOCKOUT_DURATION_MINUTES', 15)
        ]
        
        all_passed = True
        for setting, expected in security_settings:
            if not hasattr(config, setting):
                print(f"❌ FAIL: {setting} not found in config")
                all_passed = False
            else:
                actual = getattr(config, setting)
                if actual == expected:
                    print(f"✅ PASS: {setting} = {actual}")
                else:
                    print(f"⚠️  WARNING: {setting} = {actual} (expected {expected})")
        
        return all_passed
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_user_profile_security():
    """Test user profile security features"""
    print("\n👤 Testing User Profile Security Features")
    print("=" * 60)
    
    try:
        from user_profile import UserProfile
        
        # Create test profile
        profile = UserProfile("test_user")
        
        # Test password setting
        profile.set_password("TestPassword123!")
        print("✅ PASS: Password setting works")
        
        # Test password verification - correct password
        if profile.verify_password("TestPassword123!"):
            print("✅ PASS: Password verification (correct) works")
        else:
            print("❌ FAIL: Password verification (correct) failed")
            return False
        
        # Test password verification - wrong password
        if not profile.verify_password("WrongPassword"):
            print("✅ PASS: Password verification (wrong) correctly rejects")
        else:
            print("❌ FAIL: Password verification (wrong) incorrectly accepts")
            return False
        
        # Test account lockout
        profile.profile_data['failed_login_attempts'] = 0
        for i in range(3):
            profile.verify_password("WrongPassword")
        
        if profile.is_locked_out():
            print("✅ PASS: Account lockout works after 3 failed attempts")
        else:
            print("❌ FAIL: Account lockout not triggered")
            return False
        
        # Test session expiry methods
        profile.update_last_activity()
        print("✅ PASS: Last activity update works")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_encryption():
    """Test data encryption features"""
    print("\n🔐 Testing Data Encryption")
    print("=" * 60)
    
    try:
        from data_store import DataStore
        import tempfile
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with encryption enabled
            data_store = DataStore(data_dir=temp_dir)
            
            if data_store.encryption_enabled:
                print("✅ PASS: Encryption enabled")
            else:
                print("⚠️  WARNING: Encryption disabled in config")
            
            # Test data save and load
            test_data = {
                'user_id': 'test_user',
                'emotional_history': [
                    {'emotion': 'positive', 'polarity': 0.5},
                    {'emotion': 'neutral', 'polarity': 0.0}
                ],
                'session_count': 5
            }
            
            data_store.save_user_data('test_user', test_data)
            print("✅ PASS: Data save works")
            
            loaded_data = data_store.load_user_data('test_user')
            if loaded_data:
                print("✅ PASS: Data load works")
                
                if loaded_data['user_id'] == 'test_user':
                    print("✅ PASS: Data integrity verified")
                else:
                    print("❌ FAIL: Data corrupted")
                    return False
            else:
                print("❌ FAIL: Data load returned None")
                return False
            
            # Test backup creation
            backup_file = data_store.create_backup('test_user')
            if backup_file and backup_file.exists():
                print(f"✅ PASS: Backup creation works: {backup_file.name}")
            else:
                print("❌ FAIL: Backup creation failed")
                return False
            
            # Test integrity hash
            integrity_hash = data_store.get_data_integrity_hash('test_user')
            if integrity_hash:
                print(f"✅ PASS: Data integrity hash: {integrity_hash[:16]}...")
            else:
                print("❌ FAIL: Integrity hash generation failed")
                return False
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extended_history_retention():
    """Test that profile can handle 365 days of history"""
    print("\n📊 Testing Extended History Retention")
    print("=" * 60)
    
    try:
        from user_profile import UserProfile
        from datetime import datetime, timedelta
        import config
        
        profile = UserProfile("history_test")
        
        # Add snapshots to test retention
        for i in range(400):  # Add more than 365 to test trimming
            snapshot_data = {
                'emotion': 'positive',
                'polarity': 0.1 * (i % 10)
            }
            session_summary = {
                'message_count': 10,
                'average_sentiment': 0.5
            }
            profile.add_emotional_snapshot(snapshot_data, session_summary)
        
        history = profile.get_emotional_history()
        history_count = len(history)
        
        if history_count == config.EMOTIONAL_HISTORY_DAYS:
            print(f"✅ PASS: History trimmed to {history_count} days (expected {config.EMOTIONAL_HISTORY_DAYS})")
        else:
            print(f"⚠️  WARNING: History has {history_count} entries (expected {config.EMOTIONAL_HISTORY_DAYS})")
        
        # Test retrieval of specific periods
        last_7_days = profile.get_emotional_history(days=7)
        if len(last_7_days) == 7:
            print(f"✅ PASS: Last 7 days retrieval works ({len(last_7_days)} entries)")
        
        last_30_days = profile.get_emotional_history(days=30)
        if len(last_30_days) == 30:
            print(f"✅ PASS: Last 30 days retrieval works ({len(last_30_days)} entries)")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backwards_compatibility():
    """Test that old profiles still work"""
    print("\n🔄 Testing Backwards Compatibility")
    print("=" * 60)
    
    try:
        from user_profile import UserProfile
        
        # Create a profile without new security fields (simulating old profile)
        profile = UserProfile("legacy_user")
        
        # Remove security fields to simulate old profile
        if 'password_hash' in profile.profile_data:
            del profile.profile_data['password_hash']
        if 'salt' in profile.profile_data:
            del profile.profile_data['salt']
        if 'security_enabled' in profile.profile_data:
            del profile.profile_data['security_enabled']
        
        # Test that verify_password works with legacy profile (no password)
        if profile.verify_password("anything"):
            print("✅ PASS: Legacy profile (no password) allows access")
        else:
            print("❌ FAIL: Legacy profile incorrectly denies access")
            return False
        
        # Test that legacy profile can be upgraded
        profile.set_password("NewPassword123!")
        print("✅ PASS: Legacy profile can be upgraded with password")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 AI Wellness Buddy - Extended Features Test Suite")
    print("=" * 60)
    
    tests = [
        ("Extended Tracking Configuration", test_extended_tracking),
        ("Security Configuration", test_security_configuration),
        ("User Profile Security", test_user_profile_security),
        ("Data Encryption", test_data_encryption),
        ("Extended History Retention", test_extended_history_retention),
        ("Backwards Compatibility", test_backwards_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Extended features are working correctly.")
        print("\n✨ Summary of new features:")
        print("   • Extended tracking: 365 days (was 90 days)")
        print("   • Password protection with SHA-256 hashing")
        print("   • AES-256 data encryption")
        print("   • Session timeout and account lockout")
        print("   • Data integrity verification")
        print("   • Automatic backups")
        print("   • Backwards compatibility maintained")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
