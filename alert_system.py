"""
Alert system for triggering notifications when sustained distress is detected
Includes guardian notification and emergency contact features
"""

import config
from datetime import datetime


class AlertSystem:
    """Manages alerts for emotional distress and specialized support"""
    
    def __init__(self):
        self.alerts_triggered = []
        
    def trigger_distress_alert(self, pattern_summary, user_profile=None):
        """Trigger alert for sustained emotional distress"""
        alert = {
            'type': 'distress',
            'message': config.DISTRESS_ALERT_MESSAGE,
            'resources': config.GENERAL_SUPPORT_RESOURCES,
            'pattern_summary': pattern_summary,
            'timestamp': datetime.now()
        }
        
        # Check if specialized women's support should be included
        if user_profile and user_profile.get('gender') == 'female':
            if pattern_summary.get('abuse_indicators_detected'):
                alert['specialized_support'] = True
                alert['women_resources'] = config.WOMEN_SUPPORT_RESOURCES
                alert['government_resources'] = config.GOVERNMENT_WOMEN_RESOURCES
                
                # Add trusted support resources if unsafe family situation
                if user_profile.get('unsafe_contacts'):
                    alert['trusted_support'] = True
                    alert['trusted_resources'] = config.TRUSTED_SUPPORT_RESOURCES
        
        # Check if guardian alert should be triggered
        if config.ENABLE_GUARDIAN_ALERTS and user_profile:
            guardian_contacts = user_profile.get('guardian_contacts', [])
            if guardian_contacts and self._should_notify_guardians(pattern_summary):
                alert['notify_guardians'] = True
                alert['guardian_contacts'] = guardian_contacts
        
        self.alerts_triggered.append(alert)
        return alert
    
    def _should_notify_guardians(self, pattern_summary):
        """Determine if guardians should be notified based on severity"""
        if not pattern_summary:
            return False
        
        severity_level = pattern_summary.get('severity', 'low')
        threshold = config.GUARDIAN_ALERT_THRESHOLD
        
        severity_order = {'low': 0, 'medium': 1, 'high': 2}
        
        return (severity_order.get(severity_level, 0) >= 
                severity_order.get(threshold, 1))
    
    def format_guardian_notification(self, alert, user_name="User"):
        """Format notification message for guardians"""
        message = f"""
🚨 WELLNESS ALERT FOR {user_name} 🚨

This is an automated notification from AI Wellness Buddy.

{user_name} has shown signs of sustained emotional distress and may need support.

Indicators detected:
"""
        pattern_summary = alert.get('pattern_summary', {})
        
        if pattern_summary.get('sustained_distress_detected'):
            message += "  • Sustained emotional distress detected\n"
        if pattern_summary.get('abuse_indicators_detected'):
            message += "  • Potential abuse indicators present\n"
        if pattern_summary.get('consecutive_distress', 0) > 0:
            message += f"  • {pattern_summary['consecutive_distress']} consecutive distress messages\n"
        
        message += """
What you can do:
  • Reach out to check on them with care and compassion
  • Listen without judgment
  • Offer support and help them access professional resources
  • Take any mention of self-harm seriously - contact emergency services if needed

Professional Resources:
  • Crisis Hotline: 988
  • Emergency Services: 911
  • Crisis Text Line: Text HOME to 741741

This is a support tool, not a replacement for professional care.
If there is immediate danger, contact emergency services immediately.
"""
        return message
    
    def format_alert_message(self, alert, trusted_contacts=None):
        """Format alert message for display"""
        message = alert['message']
        
        # Add general resources
        message += "\n\n📞 General Support Resources:\n"
        for key, value in alert['resources'].items():
            message += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        # Add specialized women's resources if applicable
        if alert.get('specialized_support'):
            message += "\n" + config.WOMEN_SAFETY_MESSAGE
            message += "\n\n🛡️ Specialized Resources for Women:\n"
            for key, value in alert['women_resources'].items():
                message += f"  • {key.replace('_', ' ').title()}: {value}\n"
            
            # Add government resources for women
            if alert.get('government_resources'):
                message += "\n\n🏛️ Government & Legal Resources:\n"
                gov_resources = alert['government_resources']
                
                message += "\nU.S. Government Agencies:\n"
                for resource in gov_resources.get('us_govt', []):
                    message += f"  • {resource}\n"
                
                message += "\nLegal Aid:\n"
                for resource in gov_resources.get('legal_aid', []):
                    message += f"  • {resource}\n"
                
                message += "\nWomen's Mental Health:\n"
                for resource in gov_resources.get('mental_health', []):
                    message += f"  • {resource}\n"
        
        # Add trusted support resources for toxic family situations
        if alert.get('trusted_support'):
            message += "\n\n🤝 SAFE SUPPORT NETWORK 🤝\n"
            message += "\nSince family may not be safe, consider these trusted resources:\n\n"
            
            message += "Women's Organizations:\n"
            for resource in config.TRUSTED_SUPPORT_RESOURCES['women_organizations']:
                message += f"  • {resource}\n"
            
            message += "\nBuilding Safe Support:\n"
            for tip in config.TRUSTED_SUPPORT_RESOURCES['friend_support_tips']:
                message += f"  • {tip}\n"
            
            message += "\nProfessional Help:\n"
            for resource in config.TRUSTED_SUPPORT_RESOURCES['professional_support']:
                message += f"  • {resource}\n"
            
            # Show user's trusted contacts if they have added any
            if trusted_contacts:
                message += "\n💚 Your Trusted Contacts:\n"
                for contact in trusted_contacts:
                    message += f"  • {contact['name']} ({contact['relationship']})\n"
                    if contact.get('contact_info'):
                        message += f"    Contact: {contact['contact_info']}\n"
        
        # Add guardian notification info if applicable
        if alert.get('notify_guardians'):
            message += "\n\n👨‍👩‍👧‍👦 GUARDIAN NOTIFICATION\n"
            if config.AUTO_NOTIFY_GUARDIANS:
                message += "Your designated guardians/emergency contacts have been notified.\n"
            else:
                message += "Would you like to notify your designated guardians/emergency contacts?\n"
                guardian_contacts = alert.get('guardian_contacts', [])
                if guardian_contacts:
                    message += "\nYour guardians:\n"
                    for contact in guardian_contacts:
                        message += f"  • {contact.get('name', 'Unknown')} ({contact.get('relationship', 'Guardian')})\n"
        
        message += "\n💙 Remember: You are not alone, and help is available 24/7.\n"
        message += "💙 You are in control - reach out to people YOU trust.\n"
        
        return message
    
    def should_trigger_alert(self, pattern_summary):
        """Determine if an alert should be triggered based on patterns"""
        if not pattern_summary:
            return False
        
        return pattern_summary.get('sustained_distress_detected', False)
