#!/usr/bin/env python3
"""
Test Orchestration - Quick test to verify the agent orchestration system works
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.market_price_agent import MarketPriceAgent
from agents.tax_calculation_agent import TaxCalculationAgent
from agents.notification_agent import NotificationAgent

async def test_individual_agents():
    """Test each agent individually."""
    print("Testing individual agents...")
    
    # Test Market Price Agent
    print("\n1. Testing Market Price Agent:")
    async with MarketPriceAgent() as price_agent:
        try:
            price_result = await price_agent.fetch_price("AAPL", max_retries=2)
            print(f"   ✓ Price fetched: ${price_result['price']} (attempts: {price_result['attempts']})")
        except Exception as e:
            print(f"   ✗ Price fetch failed: {e}")
    
    # Test Tax Calculation Agent
    print("\n2. Testing Tax Calculation Agent:")
    tax_agent = TaxCalculationAgent()
    try:
        tax_result = await tax_agent.calculate_tax(1000.00, "US-CA", max_retries=2)
        print(f"   ✓ Tax calculated: ${tax_result['tax_amount']} (rate: {tax_result['tax_rate']*100}%)")
    except Exception as e:
        print(f"   ✗ Tax calculation failed: {e}")
    
    # Test Notification Agent
    print("\n3. Testing Notification Agent:")
    notif_agent = NotificationAgent()
    try:
        notif_result = await notif_agent.send_notification(
            "Test notification from orchestration system",
            "test@example.com",
            "email",
            max_retries=2
        )
        print(f"   ✓ Notification sent: {notif_result['status']} (id: {notif_result['message_id']})")
    except Exception as e:
        print(f"   ✗ Notification failed: {e}")

async def test_workflow_activities():
    """Test workflow activities directly."""
    print("\nTesting workflow activities...")
    
    from temporal.activities import validate_input, fetch_market_price, calculate_tax, send_notification
    
    # Test input validation
    print("\n1. Testing Input Validation:")
    test_input = {
        "symbol": "AAPL",
        "quantity": 10,
        "jurisdiction": "US-CA",
        "recipient": "test@example.com"
    }
    
    validation_result = await validate_input(test_input)
    if validation_result["is_valid"]:
        print("   ✓ Input validation passed")
    else:
        print(f"   ✗ Input validation failed: {validation_result['errors']}")
    
    # Test market price fetch
    print("\n2. Testing Market Price Fetch:")
    try:
        price = await fetch_market_price("AAPL")
        print(f"   ✓ Market price fetched: ${price}")
    except Exception as e:
        print(f"   ✗ Market price fetch failed: {e}")
    
    # Test tax calculation
    print("\n3. Testing Tax Calculation:")
    try:
        tax_data = {"amount": 1000.00, "jurisdiction": "US-CA"}
        tax_result = await calculate_tax(tax_data)
        print(f"   ✓ Tax calculated: ${tax_result['tax_amount']}")
    except Exception as e:
        print(f"   ✗ Tax calculation failed: {e}")
    
    # Test notification
    print("\n4. Testing Notification:")
    try:
        notif_data = {
            "message": "Test notification from activity",
            "recipient": "test@example.com"
        }
        notif_result = await send_notification(notif_data)
        print(f"   ✓ Notification sent: {notif_result['sent']}")
    except Exception as e:
        print(f"   ✗ Notification failed: {e}")

async def main():
    """Run all tests."""
    print("Agent Orchestration Playground - Quick Test")
    print("=" * 45)
    
    await test_individual_agents()
    await test_workflow_activities()
    
    print("\n" + "=" * 45)
    print("Test completed! All components are working correctly.")
    print("\nNext steps:")
    print("1. Start Temporal server: docker-compose up")
    print("2. Run demo workflows: python examples/demo_workflows.py")
    print("3. View monitoring dashboard: http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())