# Data Retention and Extended Patient Tracking

## 📊 AI Wellness Buddy - Long-Term Emotional Tracking Guide

This document explains how the AI Wellness Buddy tracks emotional patterns over extended periods and manages data retention.

## Table of Contents
1. [Extended Tracking Overview](#extended-tracking-overview)
2. [Data Retention Policies](#data-retention-policies)
3. [What Data is Tracked](#what-data-is-tracked)
4. [Long-Term Pattern Analysis](#long-term-pattern-analysis)
5. [Data Management](#data-management)
6. [Privacy and Compliance](#privacy-and-compliance)

---

## Extended Tracking Overview

### ✨ New Extended Tracking Features

The AI Wellness Buddy now tracks patient emotional patterns for **1 full year** (365 days) instead of the previous 90 days, providing:

✅ **Long-term trend analysis**: See how you've progressed over months
✅ **Seasonal pattern detection**: Identify patterns related to seasons, holidays
✅ **Milestone tracking**: Track progress from significant life events
✅ **Comprehensive history**: Full year of emotional wellbeing data
✅ **Better insights**: More data = more accurate pattern recognition

### Tracking Duration Comparison

| Feature | Previous | **NEW Extended** |
|---------|----------|------------------|
| Emotional History | 90 days | **365 days (1 year)** |
| Session Data | 50 messages | 50 messages |
| Conversation Archive | N/A | **180 days** |
| Backups | Manual | **Automatic** |

---

## Data Retention Policies

### Configuration Settings

The following retention periods are configurable in `config.py`:

```python
# Data retention settings
EMOTIONAL_HISTORY_DAYS = 365        # Keep 1 year of emotional history
CONVERSATION_ARCHIVE_DAYS = 180     # Archive conversations after 6 months
MAX_EMOTIONAL_SNAPSHOTS = 365       # Maximum snapshots to retain
```

### What Gets Kept and For How Long

#### 1. **Emotional History** (365 days)

**What's Stored:**
- Date and timestamp of each session
- Emotional analysis results
- Sentiment polarity scores
- Detected emotions and severity
- Distress indicators
- Abuse indicators
- Session summaries

**Retention:**
- Automatically kept for 365 days
- Oldest entries automatically removed when limit reached
- Configurable in settings

**Example Entry:**
```json
{
  "date": "2026-02-22",
  "timestamp": "2026-02-22T15:30:00",
  "emotion_data": {
    "emotion": "positive",
    "polarity": 0.5,
    "severity": "low"
  },
  "session_summary": {
    "message_count": 12,
    "average_sentiment": 0.45,
    "distress_detected": false
  }
}
```

#### 2. **Session Conversations** (Current session only)

**What's Stored:**
- Message content
- Timestamps
- Emotional analysis per message
- Pattern tracking data

**Retention:**
- During active session only
- Saved as summary in emotional history
- Full conversation not permanently stored (privacy)

#### 3. **Profile Data** (Permanent)

**What's Stored:**
- User ID and demographics
- Gender and preferences
- Trusted contacts
- Safety settings
- Creation date
- Session count

**Retention:**
- Kept as long as profile exists
- User can delete anytime

#### 4. **Security Data** (Permanent)

**What's Stored:**
- Password hash and salt
- Failed login attempts
- Lockout information
- Last activity timestamp

**Retention:**
- Kept for account security
- Reset on successful login
- Cleared on profile deletion

---

## What Data is Tracked

### Per-Session Tracking

Each session captures:

1. **Message-Level Data:**
   - Emotional sentiment (polarity: -1 to +1)
   - Emotion category (positive, neutral, negative, distress)
   - Severity level (low, medium, high)
   - Distress keywords detected
   - Abuse indicators detected

2. **Session-Level Summary:**
   - Total messages in session
   - Average sentiment
   - Distress ratio
   - Consecutive distress count
   - Emotional trend (improving, stable, declining)

3. **Temporal Data:**
   - Session date and time
   - Session duration
   - Time since last session
   - Day of week patterns

### Long-Term Pattern Tracking

Over the 365-day period, the system analyzes:

#### Weekly Patterns
- Emotional trends week over week
- Best and worst days of the week
- Consistency of check-ins

#### Monthly Patterns
- Month-to-month comparisons
- Seasonal variations
- Long-term trajectory

#### Quarterly Reviews
- 90-day trend analysis
- Major emotional shifts
- Progress milestones

#### Annual Overview
- Full year emotional journey
- Significant events correlation
- Overall wellbeing trend

---

## Long-Term Pattern Analysis

### Trend Analysis

The system provides insights on:

1. **Overall Trajectory:**
   ```
   📈 Your emotional wellbeing has been improving over the past year
   Average sentiment: +0.25 (was -0.15 at start of year)
   ```

2. **Distress Patterns:**
   ```
   📊 Distress episodes: 8 in past year
   Average duration: 3 days
   Longest streak of positive mood: 45 days
   ```

3. **Seasonal Insights:**
   ```
   🌸 Spring: Most positive (avg: +0.45)
   ❄️ Winter: Most challenging (avg: -0.10)
   ```

### Historical Comparisons

Compare different time periods:

**Example Queries:**
- "How am I doing compared to 3 months ago?"
- "What was my emotional state this time last year?"
- "Show me my best and worst months"

**Sample Output:**
```
Comparison: Current vs 6 Months Ago
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current (Last 30 days):
  Average sentiment: +0.35
  Distress ratio: 12%
  Trend: Stable

6 Months Ago (30 day period):
  Average sentiment: -0.05
  Distress ratio: 34%
  Trend: Declining

Improvement: +0.40 sentiment points ✨
```

### Milestone Tracking

Track progress from significant events:

```python
# Mark an important date
profile.add_milestone("Started therapy", date="2025-08-01")

# View progress since milestone
progress = profile.get_progress_since_milestone("Started therapy")
```

**Example Output:**
```
Progress Since "Started therapy" (205 days ago):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before: -0.20 avg sentiment, 45% distress ratio
After:  +0.30 avg sentiment, 15% distress ratio
Change: +0.50 improvement, -30% less distress ✨

Best streak: 60 consecutive days of positive mood
Total sessions: 142
```

---

## Data Management

### Viewing Your Data

**Current Session Status:**
```bash
python wellness_buddy.py
> status
```

**7-Day Summary:**
```
📊 Last 7 Days:
  Check-ins: 5
  Avg sentiment: +0.25
  Trend: Improving
```

**30-Day Summary:**
```
📊 Last 30 Days:
  Check-ins: 18
  Avg sentiment: +0.15
  Distress episodes: 2
  Trend: Stable
```

**Full Year Overview:**
```
📊 Full Year (365 days):
  Total check-ins: 243
  Avg sentiment: +0.08
  Best month: June (+0.45)
  Most challenging: January (-0.15)
  Overall trend: Improving ✨
```

### Exporting Your Data

**Export to JSON:**
```python
# Export all emotional history
history = profile.get_emotional_history()

# Save to file
import json
with open('my_wellness_journey.json', 'w') as f:
    json.dump(history, f, indent=2, default=str)
```

**Export Summary Report:**
```python
# Generate readable report
report = profile.generate_annual_report()
print(report)
```

**Example Report:**
```
AI Wellness Buddy - Annual Wellbeing Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User: [Username]
Period: March 1, 2025 - February 28, 2026

Summary:
  Total Sessions: 287
  Total Days Active: 243
  Consistency: 66% (checked in 2/3 of days)

Emotional Journey:
  Starting Point: -0.12 (February 2025)
  Current: +0.28 (February 2026)
  Overall Change: +0.40 improvement ✨

Key Milestones:
  ✨ First positive month: May 2025
  🌟 Best month: September 2025 (+0.52)
  💪 Longest positive streak: 67 days (Aug-Oct)

Insights:
  • Consistent improvement throughout year
  • Strong support network established
  • Effective coping strategies developed
  • Seasonal patterns identified and managed

Next Steps:
  • Continue current wellness practices
  • Monitor for winter seasonal patterns
  • Maintain support network connections
```

### Data Cleanup

**Remove Old Backups:**
```bash
# Keep only last 10 backups
cd ~/.wellness_buddy
ls -t *_backup_* | tail -n +11 | xargs rm
```

**Archive Old Data:**
```python
# Archive data older than 1 year to separate file
profile.archive_old_data(days=365)
```

---

## Privacy and Compliance

### Data Minimization

Despite extended tracking, we practice data minimization:

✅ **What We Store:**
- Emotional analysis summaries
- Aggregate statistics
- Trend indicators

❌ **What We Don't Store:**
- Full conversation transcripts (long-term)
- Identifying details in messages
- Unnecessary metadata

### User Control

You have complete control over your data:

**Access Your Data:**
- View anytime via status command
- Export to JSON file
- Generate reports

**Delete Your Data:**
```python
# Delete entire profile
profile.delete()

# Delete specific time period
profile.delete_history(start_date, end_date)

# Delete old backups
data_store.cleanup_backups(keep_recent=5)
```

**Adjust Retention:**
```python
# config.py - Reduce retention period
EMOTIONAL_HISTORY_DAYS = 180  # 6 months instead of 1 year

# Or increase
EMOTIONAL_HISTORY_DAYS = 730  # 2 years
```

### GDPR Compliance

For European users, the system supports GDPR rights:

1. **Right to Access**: Export all your data
2. **Right to Rectification**: Edit your data
3. **Right to Erasure**: Delete your data
4. **Right to Portability**: Export in standard JSON format
5. **Right to Object**: Disable tracking features

### Data Retention Notice

**Automatic Retention:**
- Emotional history: 365 days (rolling window)
- Older data automatically removed
- Backups kept for 30 days

**Manual Control:**
- You can delete data anytime
- You can export before deletion
- You control retention periods

---

## Configuration Guide

### Customizing Retention Periods

Edit `config.py`:

```python
# Conservative (shorter retention)
EMOTIONAL_HISTORY_DAYS = 90      # 3 months
CONVERSATION_ARCHIVE_DAYS = 30   # 1 month

# Standard (default)
EMOTIONAL_HISTORY_DAYS = 365     # 1 year
CONVERSATION_ARCHIVE_DAYS = 180  # 6 months

# Extended (longer retention)
EMOTIONAL_HISTORY_DAYS = 730     # 2 years
CONVERSATION_ARCHIVE_DAYS = 365  # 1 year

# Unlimited (use with caution)
EMOTIONAL_HISTORY_DAYS = 999999  # Effectively unlimited
# Note: File size will grow continuously
```

### Storage Considerations

**Estimated Storage Per User:**

| Duration | Approximate Size |
|----------|------------------|
| 90 days  | ~500 KB |
| 180 days | ~1 MB |
| 365 days | ~2 MB |
| 730 days | ~4 MB |

**Storage Calculation:**
```
Average entry size: ~5 KB
Entries per year: ~365
Total per year: ~1.8 MB

With encryption: ~2-3 MB per year
With backups: +20-30% (2.4-4 MB)
```

---

## Best Practices

### For Optimal Long-Term Tracking

1. **Consistent Check-ins:**
   - Daily or every other day is ideal
   - Set reminders if helpful
   - Even brief check-ins are valuable

2. **Regular Reviews:**
   - Weekly: Check 7-day summary
   - Monthly: Review monthly trends
   - Quarterly: Look at 90-day patterns
   - Annually: Generate full year report

3. **Data Hygiene:**
   - Monthly: Review and clean up old backups
   - Quarterly: Verify data integrity
   - Annually: Export full history as backup

4. **Privacy Maintenance:**
   - Enable encryption
   - Use strong password
   - Regular security reviews
   - Secure backup storage

---

## Frequently Asked Questions

**Q: Will the app slow down with 1 year of data?**
A: No, the system is optimized for performance. Even with 365 days of data, operations remain fast.

**Q: Can I import old data?**
A: Yes, data can be imported from JSON files. Contact support for migration tools.

**Q: What happens if I exceed 365 days?**
A: Oldest entries are automatically removed when the limit is reached, maintaining the rolling 365-day window.

**Q: Can I keep data forever?**
A: Yes, set `EMOTIONAL_HISTORY_DAYS = 999999` in config.py. However, consider periodic archiving for performance.

**Q: How do I migrate from 90-day to 365-day retention?**
A: Automatic. Update config.py and restart. Existing data is preserved, new data uses extended retention.

**Q: Is my historical data encrypted?**
A: Yes, if encryption is enabled, all historical data is encrypted, including backups.

---

## Summary

The AI Wellness Buddy now provides:

✅ **Extended tracking**: 365 days of emotional history
✅ **Better insights**: Long-term pattern analysis
✅ **User control**: Full data access and deletion rights
✅ **Privacy protection**: Encrypted storage, minimal data collection
✅ **Automatic management**: Old data cleanup, backup creation

Your emotional wellbeing journey is important. The extended tracking helps you see the bigger picture of your mental health progress over time. 📊💙

---

## See Also

- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Complete Features**: [COMPLETE_FEATURE_GUIDE.md](COMPLETE_FEATURE_GUIDE.md)
- **Network Deployment**: [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)
