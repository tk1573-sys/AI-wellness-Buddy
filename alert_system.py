"""
Alert system for triggering notifications when sustained distress is detected
"""

import config


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
            'pattern_summary': pattern_summary
        }
        
        # Check if specialized women's support should be included
        if user_profile and user_profile.get('gender') == 'female':
            if pattern_summary.get('abuse_indicators_detected'):
                alert['specialized_support'] = True
                alert['women_resources'] = config.WOMEN_SUPPORT_RESOURCES
                
                # Add trusted support resources if unsafe family situation
                if user_profile.get('unsafe_contacts'):
                    alert['trusted_support'] = True
                    alert['trusted_resources'] = config.TRUSTED_SUPPORT_RESOURCES
        
        self.alerts_triggered.append(alert)
        return alert
    
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
        
        message += "\n💙 Remember: You are not alone, and help is available 24/7.\n"
        message += "💙 You are in control - reach out to people YOU trust.\n"
        
        return message
    
    def should_trigger_alert(self, pattern_summary):
        """Determine if an alert should be triggered based on patterns"""
        if not pattern_summary:
            return False
        
        return pattern_summary.get('sustained_distress_detected', False)
