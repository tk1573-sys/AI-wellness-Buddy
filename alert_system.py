"""
Guardian Alert Agent — Module 5
Severity levels, escalation policy, alert logging, and consent mechanism.
"""

import config
from datetime import datetime, timedelta


# ── Severity ordering ─────────────────────────────────────────────────────────
_SEVERITY_ORDER = {level: i for i, level in enumerate(config.ALERT_SEVERITY_LEVELS)}
# e.g. INFO→0, LOW→1, MEDIUM→2, HIGH→3, CRITICAL→4


class AlertSystem:
    """
    Manages alerts for emotional distress and specialised support.

    New in Module 5:
      • Severity levels: INFO / LOW / MEDIUM / HIGH / CRITICAL
      • Escalation policy (auto-escalate if unacknowledged)
      • Alert log with timestamps (capped at MAX_ALERT_LOG_ENTRIES)
      • Consent mechanism (guardian_consent flag on alert)
    """

    def __init__(self):
        self.alerts_triggered = []   # full alert objects (backward compat)
        self.alert_log = []          # structured log for dashboard

    # ── Severity helpers ──────────────────────────────────────────────────────

    def _compute_severity(self, pattern_summary):
        """Map pattern summary to alert severity level."""
        if not pattern_summary:
            return 'INFO'
        level = pattern_summary.get('severity_level', 'LOW')
        # Further escalate if abuse indicators present
        if pattern_summary.get('abuse_indicators_detected'):
            idx = min(_SEVERITY_ORDER.get(level, 1) + 1, len(config.ALERT_SEVERITY_LEVELS) - 1)
            level = config.ALERT_SEVERITY_LEVELS[idx]
        # Critical if sustained distress + severity HIGH
        if (pattern_summary.get('sustained_distress_detected')
                and level == 'HIGH'):
            level = 'CRITICAL'
        return level

    # ── Core trigger ──────────────────────────────────────────────────────────

    def trigger_distress_alert(self, pattern_summary, user_profile=None):
        """Trigger an alert for sustained emotional distress."""
        severity = self._compute_severity(pattern_summary)
        alert = {
            'type': 'distress',
            'severity': severity,
            'message': config.DISTRESS_ALERT_MESSAGE,
            'resources': config.GENERAL_SUPPORT_RESOURCES,
            'pattern_summary': pattern_summary,
            'timestamp': datetime.now(),
            'acknowledged': False,
            'guardian_consent': False,   # user must explicitly approve guardian notification
            'escalated_at': None,
        }

        # Specialised women's support
        if user_profile and user_profile.get('gender') == 'female':
            if pattern_summary.get('abuse_indicators_detected'):
                alert['specialized_support'] = True
                alert['women_resources'] = config.WOMEN_SUPPORT_RESOURCES
                alert['government_resources'] = config.GOVERNMENT_WOMEN_RESOURCES
                if user_profile.get('unsafe_contacts'):
                    alert['trusted_support'] = True
                    alert['trusted_resources'] = config.TRUSTED_SUPPORT_RESOURCES

        # Guardian notification
        if config.ENABLE_GUARDIAN_ALERTS and user_profile:
            guardian_contacts = user_profile.get('guardian_contacts', [])
            if guardian_contacts and self._should_notify_guardians(pattern_summary):
                alert['notify_guardians'] = True
                alert['guardian_contacts'] = guardian_contacts

        self.alerts_triggered.append(alert)
        self._log_alert(alert, user_profile)
        return alert

    # ── Escalation policy ─────────────────────────────────────────────────────

    def escalate_pending_alerts(self):
        """
        Check all unacknowledged alerts and escalate severity if overdue.
        Returns list of newly escalated alerts.
        """
        escalated = []
        now = datetime.now()
        for alert in self.alerts_triggered:
            if alert.get('acknowledged'):
                continue
            current_sev = alert.get('severity', 'INFO')
            interval = config.ESCALATION_INTERVALS.get(current_sev, 60)
            if interval == 0:
                continue  # CRITICAL — no further escalation
            threshold = alert['timestamp'] + timedelta(minutes=interval)
            if now >= threshold:
                idx = _SEVERITY_ORDER.get(current_sev, 0)
                next_sev = config.ALERT_SEVERITY_LEVELS[min(idx + 1, len(config.ALERT_SEVERITY_LEVELS) - 1)]
                alert['severity'] = next_sev
                alert['escalated_at'] = now
                escalated.append(alert)
        return escalated

    def acknowledge_alert(self, alert):
        """Mark an alert as acknowledged (consent mechanism)."""
        alert['acknowledged'] = True
        alert['acknowledged_at'] = datetime.now()

    def grant_guardian_consent(self, alert):
        """User explicitly consents to notify guardians."""
        alert['guardian_consent'] = True

    # ── Alert log ────────────────────────────────────────────────────────────

    def _log_alert(self, alert, user_profile=None):
        """Append a structured log entry for the dashboard."""
        entry = {
            'timestamp': alert['timestamp'],
            'severity': alert['severity'],
            'type': alert['type'],
            'sustained_distress': alert.get('pattern_summary', {}).get('sustained_distress_detected', False),
            'abuse_indicators': alert.get('pattern_summary', {}).get('abuse_indicators_detected', False),
            'severity_score': alert.get('pattern_summary', {}).get('severity_score', 0),
            'notify_guardians': alert.get('notify_guardians', False),
            'acknowledged': alert.get('acknowledged', False),
            'user': user_profile.get('user_id', 'unknown') if user_profile else 'unknown',
        }
        self.alert_log.append(entry)
        # Cap log size
        if len(self.alert_log) > config.MAX_ALERT_LOG_ENTRIES:
            self.alert_log = self.alert_log[-config.MAX_ALERT_LOG_ENTRIES:]

    def get_alert_log(self):
        """Return the structured alert log for dashboard display."""
        return list(self.alert_log)

    # ── Trigger condition ────────────────────────────────────────────────────

    def should_trigger_alert(self, pattern_summary):
        """Determine if an alert should be triggered based on patterns."""
        if not pattern_summary:
            return False
        return pattern_summary.get('sustained_distress_detected', False)

    def _should_notify_guardians(self, pattern_summary):
        """Determine if guardians should be notified based on sustained distress detection."""
        if not pattern_summary:
            return False
        return pattern_summary.get('sustained_distress_detected', False)

    # ── Formatting (backward-compatible) ─────────────────────────────────────

    def format_guardian_notification(self, alert, user_name="User"):
        """Format notification message for guardians."""
        severity = alert.get('severity', 'MEDIUM')
        message = f"\n🚨 WELLNESS ALERT [{severity}] FOR {user_name} 🚨\n\n"
        message += "This is an automated notification from AI Wellness Buddy.\n\n"
        message += f"{user_name} has shown signs of sustained emotional distress and may need support.\n\n"
        message += "Indicators detected:\n"
        ps = alert.get('pattern_summary', {})
        if ps.get('sustained_distress_detected'):
            message += "  • Sustained emotional distress detected\n"
        if ps.get('abuse_indicators_detected'):
            message += "  • Potential abuse indicators present\n"
        if ps.get('consecutive_distress', 0) > 0:
            message += f"  • {ps['consecutive_distress']} consecutive distress messages\n"
        if ps.get('severity_score'):
            message += f"  • Severity score: {ps['severity_score']:.1f}/10\n"
        message += """
What you can do:
  • Reach out to check on them with care and compassion
  • Listen without judgment
  • Offer support and help them access professional resources
  • Take any mention of self-harm seriously — contact emergency services if needed

Professional Resources:
  • Crisis Hotline: 988
  • Emergency Services: 911
  • Crisis Text Line: Text HOME to 741741

This is a support tool, not a replacement for professional care.
If there is immediate danger, contact emergency services immediately.
"""
        return message

    def format_alert_message(self, alert, trusted_contacts=None):
        """Format alert message for display (backward-compatible)."""
        severity = alert.get('severity', 'MEDIUM')
        message = f"**🔴 Alert Level: {severity}**\n"
        message += alert['message']

        message += "\n\n📞 General Support Resources:\n"
        for key, value in alert['resources'].items():
            message += f"  • {key.replace('_', ' ').title()}: {value}\n"

        if alert.get('specialized_support'):
            message += "\n" + config.WOMEN_SAFETY_MESSAGE
            message += "\n\n🛡️ Specialised Resources for Women:\n"
            for key, value in alert['women_resources'].items():
                message += f"  • {key.replace('_', ' ').title()}: {value}\n"
            if alert.get('government_resources'):
                gov = alert['government_resources']
                message += "\n\n🏛️ Government & Legal Resources:\n"
                for r in gov.get('us_govt', []):
                    message += f"  • {r}\n"
                for r in gov.get('legal_aid', []):
                    message += f"  • {r}\n"
                for r in gov.get('mental_health', []):
                    message += f"  • {r}\n"

        if alert.get('trusted_support'):
            message += "\n\n🤝 SAFE SUPPORT NETWORK 🤝\n"
            message += "\nSince family may not be safe, consider these trusted resources:\n\n"
            for r in config.TRUSTED_SUPPORT_RESOURCES['women_organizations']:
                message += f"  • {r}\n"
            for tip in config.TRUSTED_SUPPORT_RESOURCES['friend_support_tips']:
                message += f"  • {tip}\n"
            for r in config.TRUSTED_SUPPORT_RESOURCES['professional_support']:
                message += f"  • {r}\n"
            if trusted_contacts:
                message += "\n💚 Your Trusted Contacts:\n"
                for c in trusted_contacts:
                    message += f"  • {c['name']} ({c['relationship']})\n"
                    if c.get('contact_info'):
                        message += f"    Contact: {c['contact_info']}\n"

        if alert.get('notify_guardians'):
            message += "\n\n👨‍👩‍👧‍👦 GUARDIAN NOTIFICATION\n"
            if not alert.get('guardian_consent'):
                message += ("⚠️ Your guardian contacts are listed below. "
                            "Use the **Guardian Alerts** tab to consent to notify them.\n")
            else:
                message += "✅ You have consented to notify your guardians.\n"
            for c in alert.get('guardian_contacts', []):
                message += f"  • {c.get('name')} ({c.get('relationship')})"
                if c.get('contact_info'):
                    message += f" — {c['contact_info']}"
                message += "\n"

        message += "\n💙 Remember: You are not alone, and help is available 24/7.\n"
        message += "💙 You are in control — reach out to people YOU trust.\n"
        return message
