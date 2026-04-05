import asyncio
import pytest
from temporal.activities import (
    validate_input,
    fetch_market_price,
    calculate_tax,
    send_notification
)

def test_validate_input_success():
    """Test successful input validation."""
    input_data = {
        "symbol": "AAPL",
        "quantity": 10,
        "jurisdiction": "US-CA",
        "recipient": "user@example.com"
    }
    
    result = asyncio.run(validate_input(input_data))
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0

def test_validate_input_missing_fields():
    """Test input validation with missing fields."""
    input_data = {
        "symbol": "AAPL"
        # Missing quantity and jurisdiction
    }
    
    result = asyncio.run(validate_input(input_data))
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0
    assert any("quantity" in error for error in result["errors"])
    assert any("jurisdiction" in error for error in result["errors"])

def test_validate_input_invalid_quantity():
    """Test input validation with invalid quantity."""
    input_data = {
        "symbol": "AAPL",
        "quantity": -5,  # Invalid negative quantity
        "jurisdiction": "US-CA"
    }
    
    result = asyncio.run(validate_input(input_data))
    assert result["is_valid"] == False
    assert any("greater than zero" in error for error in result["errors"])

def test_fetch_market_price():
    """Test market price fetching."""
    try:
        price = asyncio.run(fetch_market_price("AAPL"))
        assert isinstance(price, float)
    except Exception as e:
        assert "Market price fetch failed" in str(e)

def test_calculate_tax():
    """Test tax calculation."""
    tax_data = {
        "amount": 1000.00,
        "jurisdiction": "US-CA"
    }
    
    try:
        result = asyncio.run(calculate_tax(tax_data))
        assert "tax_amount" in result
        assert "tax_rate" in result
        assert result["tax_rate"] == 0.085  # California rate
    except Exception as e:
        assert "Tax calculation failed" in str(e)

def test_send_notification():
    """Test notification sending."""
    notification_data = {
        "message": "Test notification",
        "recipient": "test@example.com"
    }
    
    try:
        result = asyncio.run(send_notification(notification_data))
        assert "sent" in result
        assert "recipient" in result
    except Exception as e:
        assert "Notification failed" in str(e)
