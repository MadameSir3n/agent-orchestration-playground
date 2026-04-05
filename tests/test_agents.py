import pytest
import asyncio
from agents.market_price_agent import MarketPriceAgent
from agents.tax_calculation_agent import TaxCalculationAgent
from agents.notification_agent import NotificationAgent

@pytest.mark.asyncio
async def test_market_price_agent():
    """Test market price agent functionality."""
    async with MarketPriceAgent() as agent:
        # Test successful price fetch
        result = await agent.fetch_price("AAPL")
        assert result["symbol"] == "AAPL"
        assert isinstance(result["price"], float)
        assert result["price"] > 0
        assert "timestamp" in result

@pytest.mark.asyncio
async def test_market_price_agent_retry():
    """Test market price agent retry logic."""
    agent = MarketPriceAgent()
    
    # This should succeed after retries
    result = await agent.fetch_price("GOOGL", max_retries=5)
    assert result["symbol"] == "GOOGL"
    assert result["attempts"] >= 1

@pytest.mark.asyncio
async def test_tax_calculation_agent():
    """Test tax calculation agent functionality."""
    agent = TaxCalculationAgent()
    
    # Test tax calculation
    result = await agent.calculate_tax(1000.00, "US-CA")
    assert result["amount"] == 1000.00
    assert result["jurisdiction"] == "US-CA"
    assert result["tax_rate"] == 0.085
    assert result["tax_amount"] == 85.00
    assert result["total_with_tax"] == 1085.00

@pytest.mark.asyncio
async def test_tax_calculation_agent_default_rate():
    """Test tax calculation with default rate."""
    agent = TaxCalculationAgent()
    
    # Test with unknown jurisdiction (should use default 5%)
    result = await agent.calculate_tax(1000.00, "UNKNOWN")
    assert result["tax_rate"] == 0.05
    assert result["tax_amount"] == 50.00

@pytest.mark.asyncio
async def test_notification_agent():
    """Test notification agent functionality."""
    agent = NotificationAgent()
    
    # Test single notification
    result = await agent.send_notification(
        "Test message",
        "test@example.com",
        "email"
    )
    
    assert result["status"] == "sent"
    assert result["recipient"] == "test@example.com"
    assert "idempotency_key" in result

@pytest.mark.asyncio
async def test_notification_agent_idempotency():
    """Test notification agent idempotency."""
    agent = NotificationAgent()
    
    # Send same notification twice
    result1 = await agent.send_notification(
        "Test message",
        "test@example.com",
        "email",
        idempotency_key="test-key-123"
    )
    
    result2 = await agent.send_notification(
        "Test message",
        "test@example.com",
        "email",
        idempotency_key="test-key-123"
    )
    
    assert result1["status"] == "sent"
    assert result2["status"] == "duplicate"

@pytest.mark.asyncio
async def test_notification_agent_bulk():
    """Test bulk notification sending."""
    agent = NotificationAgent()
    
    notifications = [
        {
            "message": "Message 1",
            "recipient": "user1@example.com",
            "channel": "email"
        },
        {
            "message": "Message 2", 
            "recipient": "user2@example.com",
            "channel": "sms"
        }
    ]
    
    result = await agent.send_bulk_notifications(notifications)
    
    assert result["total_sent"] >= 0
    assert isinstance(result["results"], list)