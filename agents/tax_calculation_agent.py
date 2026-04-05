#!/usr/bin/env python3
"""
Tax Calculation Agent - Calculates taxes with jurisdiction awareness
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxCalculationAgent:
    """Agent for calculating taxes with retry logic and jurisdiction handling."""
    
    def __init__(self):
        # Tax rates by jurisdiction
        self.tax_rates = {
            "US-CA": 0.085,    # California
            "US-NY": 0.0925,   # New York
            "US-TX": 0.0625,   # Texas
            "US-FL": 0.06,     # Florida
            "US-WA": 0.065,    # Washington
            "EU-DE": 0.19,     # Germany
            "EU-FR": 0.20,     # France
            "EU-GB": 0.20,     # United Kingdom
            "EU-NL": 0.21,     # Netherlands
            "CN-SH": 0.13,     # China (Shanghai)
            "JP-13": 0.10      # Japan (Tokyo)
        }
    
    async def calculate_tax(self, amount: float, jurisdiction: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Calculate tax for an amount in a specific jurisdiction.
        
        Args:
            amount: Amount to calculate tax on
            jurisdiction: Jurisdiction code (e.g., "US-CA")
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with tax calculation results
        """
        for attempt in range(max_retries + 1):
            try:
                # Simulate network delay
                await asyncio.sleep(random.uniform(0.05, 0.2))
                
                # Simulate occasional service failures (3% failure rate)
                if random.random() < 0.03:
                    raise Exception("Tax service temporarily unavailable")
                
                # Simulate rate limiting (1% rate limit hits)
                if random.random() < 0.01:
                    raise Exception("Rate limit exceeded")
                
                # Calculate tax
                tax_rate = self.tax_rates.get(jurisdiction, 0.05)  # Default 5%
                tax_amount = amount * tax_rate
                
                return {
                    "amount": amount,
                    "jurisdiction": jurisdiction,
                    "tax_rate": tax_rate,
                    "tax_amount": round(tax_amount, 2),
                    "total_with_tax": round(amount + tax_amount, 2),
                    "calculation_timestamp": datetime.now().isoformat(),
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Failed to calculate tax after {max_retries} attempts: {str(e)}")
                    raise
                
                # Exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time:.2f}s: {str(e)}")
                await asyncio.sleep(wait_time)
        
        raise Exception("Max retries exceeded")
    
    async def get_tax_rates(self) -> Dict[str, float]:
        """Get all available tax rates."""
        return self.tax_rates.copy()

# Example usage
async def main():
    """Example usage of the TaxCalculationAgent."""
    agent = TaxCalculationAgent()
    
    try:
        result = await agent.calculate_tax(1000.00, "US-CA")
        print(f"Tax calculation result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())