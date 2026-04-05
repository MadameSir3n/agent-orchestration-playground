#!/usr/bin/env python3
"""
Notification Agent - Sends notifications with idempotency and reliability
"""

import asyncio
import logging
from typing import Dict, Any, Set
from datetime import datetime
import random
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationAgent:
    """Agent for sending notifications with idempotency and retry handling."""
    
    def __init__(self):
        # Track sent notifications for idempotency
        self.sent_notifications: Set[str] = set()
        # Simulated delivery failures
        self.delivery_failures = {
            "email": 0.02,  # 2% email failure rate
            "sms": 0.05,    # 5% SMS failure rate
            "push": 0.01    # 1% push notification failure rate
        }
    
    async def send_notification(self, message: str, recipient: str, channel: str = "email", 
                              max_retries: int = 3, idempotency_key: str = None) -> Dict[str, Any]:
        """
        Send a notification with reliability patterns.
        
        Args:
            message: Notification message content
            recipient: Recipient identifier
            channel: Notification channel (email, sms, push)
            max_retries: Maximum number of retry attempts
            idempotency_key: Unique key to prevent duplicate sends
            
        Returns:
            Dictionary with notification results
        """
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = self._generate_idempotency_key(message, recipient, channel)
        
        # Check if already sent (idempotency)
        if idempotency_key in self.sent_notifications:
            logger.info(f"Notification already sent (idempotency): {idempotency_key}")
            return {
                "status": "duplicate",
                "idempotency_key": idempotency_key,
                "message": "Notification already sent",
                "timestamp": datetime.now().isoformat()
            }
        
        for attempt in range(max_retries + 1):
            try:
                # Simulate network delay
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
                # Simulate delivery failures based on channel
                failure_rate = self.delivery_failures.get(channel, 0.03)
                if random.random() < failure_rate:
                    raise Exception(f"{channel.capitalize()} delivery failed")
                
                # Simulate rate limiting (0.5% rate limit hits)
                if random.random() < 0.005:
                    raise Exception("Notification service rate limit exceeded")
                
                # Mark as sent (idempotency)
                self.sent_notifications.add(idempotency_key)
                
                return {
                    "status": "sent",
                    "idempotency_key": idempotency_key,
                    "message_id": f"msg-{int(datetime.now().timestamp() * 1000000)}",
                    "recipient": recipient,
                    "channel": channel,
                    "message": message[:100] + "..." if len(message) > 100 else message,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Failed to send notification after {max_retries} attempts: {str(e)}")
                    # Still mark as attempted to prevent infinite retries
                    self.sent_notifications.add(idempotency_key)
                    raise
                
                # Exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time:.2f}s: {str(e)}")
                await asyncio.sleep(wait_time)
        
        raise Exception("Max retries exceeded")
    
    def _generate_idempotency_key(self, message: str, recipient: str, channel: str) -> str:
        """Generate a unique idempotency key."""
        key_data = f"{message}|{recipient}|{channel}|{datetime.now().date().isoformat()}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def send_bulk_notifications(self, notifications: list, max_concurrent: int = 10) -> Dict[str, Any]:
        """
        Send multiple notifications concurrently with rate limiting.
        
        Args:
            notifications: List of notification dictionaries
            max_concurrent: Maximum number of concurrent sends
            
        Returns:
            Dictionary with bulk send results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        failures = []
        
        async def send_single(notification):
            async with semaphore:
                try:
                    result = await self.send_notification(**notification)
                    results.append(result)
                except Exception as e:
                    failures.append({
                        "notification": notification,
                        "error": str(e)
                    })
        
        # Send all notifications concurrently
        tasks = [send_single(notif) for notif in notifications]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "total_sent": len(results),
            "total_failed": len(failures),
            "results": results,
            "failures": failures,
            "timestamp": datetime.now().isoformat()
        }

# Example usage
async def main():
    """Example usage of the NotificationAgent."""
    agent = NotificationAgent()
    
    try:
        # Single notification
        result = await agent.send_notification(
            "Your trade has been executed successfully",
            "user@example.com",
            "email"
        )
        print(f"Notification result: {result}")
        
        # Bulk notifications
        notifications = [
            {
                "message": "Price alert: AAPL reached $150",
                "recipient": "user1@example.com",
                "channel": "email"
            },
            {
                "message": "Portfolio update available",
                "recipient": "user2@example.com", 
                "channel": "sms"
            }
        ]
        
        bulk_result = await agent.send_bulk_notifications(notifications)
        print(f"Bulk notification result: {bulk_result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())