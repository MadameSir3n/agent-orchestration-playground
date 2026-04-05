from temporalio import activity
from typing import Dict, Any
import asyncio
import logging
import random
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulated third-party service clients
class MarketDataService:
    """Simulated market data service with occasional failures."""
    
    async def get_price(self, symbol: str) -> float:
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simulate occasional failures (5% failure rate)
        if random.random() < 0.05:
            raise Exception(f"Market data service unavailable for {symbol}")
        
        # Return simulated price
        base_prices = {
            "AAPL": 150.00,
            "GOOGL": 2500.00,
            "MSFT": 300.00,
            "AMZN": 3200.00,
            "TSLA": 200.00
        }
        return base_prices.get(symbol, 100.00) * random.uniform(0.95, 1.05)

class TaxService:
    """Simulated tax calculation service."""
    
    async def calculate(self, amount: float, jurisdiction: str) -> Dict[str, Any]:
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Simulate occasional rate limiting (2% rate limit rate)
        if random.random() < 0.02:
            raise Exception("Rate limit exceeded")
        
        # Calculate tax based on jurisdiction
        tax_rates = {
            "US-CA": 0.085,  # California
            "US-NY": 0.0925, # New York
            "US-TX": 0.0625, # Texas
            "EU-DE": 0.19,   # Germany
            "EU-FR": 0.20    # France
        }
        
        tax_rate = tax_rates.get(jurisdiction, 0.05)  # Default 5%
        tax_amount = amount * tax_rate
        
        return {
            "tax_amount": round(tax_amount, 2),
            "tax_rate": tax_rate,
            "jurisdiction": jurisdiction
        }

class NotificationService:
    """Simulated notification service."""
    
    async def send(self, message: str, recipient: str) -> Dict[str, Any]:
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Simulate occasional failures (3% failure rate)
        if random.random() < 0.03:
            raise Exception("Notification service temporarily unavailable")
        
        return {
            "sent": True,
            "recipient": recipient,
            "message_id": f"msg-{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat()
        }

# Initialize services
market_service = MarketDataService()
tax_service = TaxService()
notification_service = NotificationService()

@activity.defn
async def validate_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input data for the workflow."""
    logger.info("Validating input data")
    
    errors = []
    
    # Check required fields
    required_fields = ["symbol", "quantity", "jurisdiction"]
    for field in required_fields:
        if field not in input_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate quantity
    if "quantity" in input_data:
        try:
            quantity = float(input_data["quantity"])
            if quantity <= 0:
                errors.append("Quantity must be greater than zero")
        except ValueError:
            errors.append("Quantity must be a valid number")
    
    # Validate symbol
    if "symbol" in input_data:
        symbol = input_data["symbol"]
        if not isinstance(symbol, str) or len(symbol) < 1:
            errors.append("Symbol must be a non-empty string")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

@activity.defn
async def fetch_market_price(symbol: str) -> float:
    """Fetch market price for a symbol with retry logic."""
    logger.info(f"Fetching market price for {symbol}")
    
    try:
        price = await market_service.get_price(symbol)
        logger.info(f"Retrieved price {price} for {symbol}")
        return price
    except Exception as e:
        logger.error(f"Failed to fetch market price: {str(e)}")
        raise activity.ApplicationError(f"Market price fetch failed: {str(e)}")

@activity.defn
async def calculate_tax(tax_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate tax for an amount in a jurisdiction."""
    logger.info(f"Calculating tax for {tax_data}")
    
    try:
        amount = tax_data["amount"]
        jurisdiction = tax_data["jurisdiction"]
        result = await tax_service.calculate(amount, jurisdiction)
        logger.info(f"Calculated tax: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to calculate tax: {str(e)}")
        raise activity.ApplicationError(f"Tax calculation failed: {str(e)}")

@activity.defn
async def send_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send notification with idempotency."""
    logger.info(f"Sending notification: {notification_data}")
    
    try:
        message = notification_data["message"]
        recipient = notification_data["recipient"]
        result = await notification_service.send(message, recipient)
        logger.info(f"Notification sent: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise activity.ApplicationError(f"Notification failed: {str(e)}")