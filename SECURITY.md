# Security Features and Best Practices

## 🔒 AI Wellness Buddy Security Guide

This document explains all security features implemented in the AI Wellness Buddy and provides best practices for secure usage.

## Table of Contents
1. [Security Features Overview](#security-features-overview)
2. [Profile Password Protection](#profile-password-protection)
3. [Data Encryption](#data-encryption)
4. [Session Management](#session-management)
5. [Account Lockout Protection](#account-lockout-protection)
6. [Data Integrity](#data-integrity)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Security Features Overview

The AI Wellness Buddy includes multiple layers of security to protect your sensitive emotional health data:

### ✅ Security Features
- **Password Protection**: Optional password/PIN for profile access
- **Data Encryption**: AES-256 encryption for data at rest
- **Session Timeout**: Automatic logout after inactivity
- **Account Lockout**: Protection against brute force attacks
- **Data Integrity**: SHA-256 hashing for data verification
- **File Permissions**: Owner-only access to data files (Unix/Linux)
- **XSRF Protection**: Cross-site request forgery protection for web UI
- **Backup System**: Automatic backups before critical operations

---

## Profile Password Protection

### Setting a Password

When creating a new profile or accessing an existing one, you can set a password:

```python
# The system will prompt you to set a password
Enter password (min 8 characters): ********
Confirm password: ********
```

**Password Requirements:**
- Minimum length: 8 characters
- Recommended: Mix of letters, numbers, and symbols
- Avoid: Personal information (name, birthdate, etc.)

### How It Works

1. **Password Hashing**: Passwords are never stored in plain text
2. **Salt Generation**: Each password gets a unique random salt
3. **SHA-256 Hashing**: Password + salt are hashed using SHA-256
4. **Secure Storage**: Only the hash and salt are stored

**Example of what's stored:**
```json
{
  "password_hash": "a7b3c4d5e6f7...",
  "salt": "9f8e7d6c5b4a...",
  "security_enabled": true
}
```

### Disabling Password Protection

You can disable password protection if you're using the app in a secure, private environment:

```python
# Set ENABLE_PROFILE_PASSWORD = False in config.py
ENABLE_PROFILE_PASSWORD = False
```

---

## Data Encryption

### Encryption at Rest

All user data can be encrypted when stored on disk using industry-standard AES-256 encryption.

**How It Works:**

1. **Key Generation**: A unique encryption key is generated for your installation
2. **Fernet Encryption**: Uses symmetric encryption (AES-256 in CBC mode)
3. **Encrypted Storage**: All profile data is encrypted before writing to disk
4. **Secure Key Storage**: Encryption key is stored in `.wellness_buddy/.encryption_key` with restricted permissions

**File Structure:**
```
~/.wellness_buddy/
├── .encryption_key          # Encryption key (600 permissions)
├── username.json            # Encrypted user data
└── username_backup_*.json   # Encrypted backups
```

### Enabling/Disabling Encryption

**To enable encryption** (enabled by default):
```python
# In config.py
ENABLE_DATA_ENCRYPTION = True
```

**To disable encryption** (not recommended):
```python
# In config.py
ENABLE_DATA_ENCRYPTION = False
```

### Migration from Unencrypted Data

The system automatically handles migration:
- Old unencrypted profiles can still be loaded
- Data will be encrypted on next save
- No manual intervention required

### Encryption Key Management

⚠️ **IMPORTANT**: The encryption key is critical!

**Backup Your Key:**
```bash
# Copy the encryption key to a secure location
cp ~/.wellness_buddy/.encryption_key ~/secure_backup/
```

**Lost Key = Lost Data:**
- If you lose the encryption key, data cannot be decrypted
- Keep a secure backup of your `.encryption_key` file
- Store backup in a password manager or encrypted drive

---

## Session Management

### Automatic Session Timeout

To protect against unauthorized access if you leave your device unattended:

**Configuration:**
```python
# config.py
SESSION_TIMEOUT_MINUTES = 30  # Auto-logout after 30 minutes of inactivity
```

**How It Works:**
- System tracks last activity timestamp
- If inactivity exceeds timeout, session expires
- User must log in again with password
- Activity is updated on each interaction

**Disable Timeout:**
```python
SESSION_TIMEOUT_MINUTES = 0  # Disabled
```

---

## Account Lockout Protection

Protection against brute force password attacks:

**Configuration:**
```python
# config.py
MAX_LOGIN_ATTEMPTS = 3          # Lock after 3 failed attempts
LOCKOUT_DURATION_MINUTES = 15   # Lock for 15 minutes
```

**How It Works:**

1. **Failed Login Tracking**: System counts failed password attempts
2. **Automatic Lockout**: After 3 failed attempts, account is locked
3. **Timed Lockout**: Account unlocks automatically after 15 minutes
4. **Reset on Success**: Successful login resets failed attempt counter

**Locked Out?**
```
Account is locked due to multiple failed login attempts.
Please try again in 14 minutes.
```

**Manual Unlock** (if you have file system access):
```python
# Edit the user's .json file and remove:
"failed_login_attempts": 0,
"lockout_until": null
```

---

## Data Integrity

### SHA-256 Integrity Checks

The system can verify data integrity using SHA-256 hashing:

```python
# Get integrity hash of user data
hash = data_store.get_data_integrity_hash(user_id)

# Store this hash to verify data hasn't been tampered with
```

### Automatic Backups

Before critical operations, the system creates timestamped backups:

```python
# Creates backup like: username_backup_20260222_153000.json
backup_file = data_store.create_backup(user_id)
```

**Backup Location:**
```
~/.wellness_buddy/
├── username.json
├── username_backup_20260222_153000.json
├── username_backup_20260221_142030.json
└── ...
```

---

## Best Practices

### 🔐 Strong Password Guidelines

1. **Length**: Use at least 12 characters
2. **Complexity**: Mix uppercase, lowercase, numbers, symbols
3. **Uniqueness**: Don't reuse passwords from other services
4. **Avoid**: Personal information, dictionary words, common patterns

**Examples:**
- ❌ Weak: `password123`, `myname2024`
- ✅ Strong: `W3ll-B3ing!2024#Secure`, `Emot!0n@lH3alth$99`

### 🖥️ Device Security

1. **Lock Your Device**: Always lock your computer/phone when away
2. **Private Environment**: Use in a private, trusted environment
3. **Secure Network**: Avoid public Wi-Fi for sensitive conversations
4. **Up-to-Date Software**: Keep your operating system updated

### 💾 Data Protection

1. **Regular Backups**: Manually backup `~/.wellness_buddy/` directory
2. **Secure Storage**: Use encrypted drives or cloud storage with encryption
3. **Key Backup**: Keep encryption key backup in password manager
4. **Access Control**: Limit who can access your computer/account

### 🌐 Network Security

When using network/web UI:

1. **Trusted Networks Only**: Use only on home or trusted networks
2. **HTTPS**: Use HTTPS for internet-facing deployments
3. **Firewall**: Configure firewall to restrict access
4. **VPN**: Use VPN for remote access instead of exposing to internet

### 🗑️ Data Deletion

When you're done with the app:

1. **Delete Profile**: Use the profile deletion feature in the app
2. **Manual Cleanup**: Remove `~/.wellness_buddy/` directory
3. **Secure Deletion**: Use secure delete tools for sensitive data

```bash
# Secure deletion (Linux/Mac)
rm -rf ~/.wellness_buddy/
# Or use secure deletion tools
shred -vfz -n 10 ~/.wellness_buddy/*
```

---

## Troubleshooting

### Forgot Password?

**Option 1: Reset via file system** (if you have access)
```bash
# Edit the user's JSON file
nano ~/.wellness_buddy/username.json

# Remove or reset these fields:
"password_hash": null,
"salt": null,
"security_enabled": false,
"failed_login_attempts": 0,
"lockout_until": null
```

**Option 2: Delete and recreate profile**
- Note: This loses all emotional history
- Backup data first if needed for records

### Encryption Key Lost?

If you lose `.encryption_key`:

❌ **Data is permanently unrecoverable**

**Prevention:**
- Backup `.encryption_key` to secure location
- Store in password manager
- Keep encrypted cloud backup

### Can't Load Profile?

**Possible causes:**
1. Wrong encryption key
2. Corrupted data file
3. Incorrect permissions

**Solutions:**
```bash
# Check file permissions
ls -l ~/.wellness_buddy/

# Should show: -rw------- (600)
# Fix if needed:
chmod 600 ~/.wellness_buddy/*

# Try loading a backup
cp ~/.wellness_buddy/username_backup_*.json ~/.wellness_buddy/username.json
```

### Session Keeps Timing Out?

Increase timeout duration:
```python
# config.py
SESSION_TIMEOUT_MINUTES = 60  # 1 hour
# or
SESSION_TIMEOUT_MINUTES = 0   # Disable
```

---

## Security Audit Log

The system logs important security events:

**Events Logged:**
- Failed login attempts
- Successful logins
- Account lockouts
- Password changes
- Data access
- Profile deletions

**Log Location:**
```
~/.wellness_buddy/security_audit.log
```

---

## Compliance and Privacy

### HIPAA Compliance Notes

While this app includes strong security features, for HIPAA compliance in a clinical setting:

⚠️ **Additional Requirements:**
- Business Associate Agreement (BAA) with cloud providers
- Encrypted transmission (HTTPS/TLS)
- Access controls and audit logs
- Incident response procedures
- Physical security of servers

### Privacy Features

✅ **What We Do:**
- All data stored locally on your device
- No external API calls or cloud storage
- No telemetry or analytics
- No data sharing

❌ **What We Don't Do:**
- Don't send data to external servers
- Don't track usage
- Don't share with third parties
- Don't access your data without your password

---

## Security Updates

### Reporting Security Issues

If you discover a security vulnerability:

1. **Don't** open a public issue
2. **Do** report privately to repository maintainers
3. Include details of the vulnerability
4. Allow time for patch before disclosure

### Keeping Secure

1. **Update Regularly**: Keep the app updated to latest version
2. **Review Changes**: Read release notes for security updates
3. **Monitor Dependencies**: Check for security updates in dependencies

---

## Summary Checklist

Before using AI Wellness Buddy in production:

- [ ] Set a strong password for your profile
- [ ] Verify encryption is enabled (`ENABLE_DATA_ENCRYPTION = True`)
- [ ] Backup your encryption key to a secure location
- [ ] Configure appropriate session timeout
- [ ] Use on trusted networks only
- [ ] Enable firewall protection
- [ ] Set up regular backups
- [ ] Review file permissions (should be 600)
- [ ] Keep software updated
- [ ] Use HTTPS for network deployments

---

## Additional Resources

- **Network Security**: See [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)
- **Data Retention**: See [DATA_RETENTION.md](DATA_RETENTION.md)
- **Feature Guide**: See [COMPLETE_FEATURE_GUIDE.md](COMPLETE_FEATURE_GUIDE.md)

---

**Remember**: Security is a shared responsibility. While the app provides strong security features, you must also:
- Use strong passwords
- Keep your device secure
- Use trusted networks
- Backup your data
- Keep software updated

Your emotional wellbeing data is sensitive and personal. Treat it with the care it deserves. 💙🔒
