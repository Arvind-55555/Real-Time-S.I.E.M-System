import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationHandler:
    def __init__(self, config=None):
        self.config = config or {}
        self.email_enabled = self.config.get('notifications.email.enabled', False)
        self.slack_enabled = self.config.get('notifications.slack.enabled', False)
        self.webhook_enabled = self.config.get('notifications.webhook.enabled', False)
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        try:
            sent = False
            
            if self.email_enabled:
                self._send_email(alert)
                sent = True
            
            if self.slack_enabled:
                self._send_slack(alert)
                sent = True
            
            if self.webhook_enabled:
                self._send_webhook(alert)
                sent = True
            
            if sent:
                logger.info(f"Alert notification sent: {alert.get('alert_id', 'unknown')}")
            else:
                logger.debug(f"No notification channels enabled for alert: {alert.get('alert_id', 'unknown')}")
            
            return sent
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
            return False
    
    def _send_email(self, alert: Dict[str, Any]):
        logger.debug(f"Email notification: {alert.get('alert_id')} - {alert.get('severity')}")
    
    def _send_slack(self, alert: Dict[str, Any]):
        logger.debug(f"Slack notification: {alert.get('alert_id')} - {alert.get('severity')}")
    
    def _send_webhook(self, alert: Dict[str, Any]):
        logger.debug(f"Webhook notification: {alert.get('alert_id')} - {alert.get('severity')}")
