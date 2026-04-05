#!/usr/bin/env python3
"""
Market Price Agent - Fetches market prices with reliability patterns
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketPriceAgent:
    """Agent for fetching market prices with retry and rate limiting handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = None
        self.rate_limit_remaining = 100  # Simulated rate limit
        self.rate_limit_reset = datetime.now()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_price(self, symbol: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Fetch market price for a symbol with retry logic and rate limiting.
        
        Args:
            symbol: Stock symbol to fetch price for
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with price data and metadata
        """
        for attempt in range(max_retries + 1):
            try:
                # Check rate limit
                if not await self._check_rate_limit():
                    wait_time = (self.rate_limit_reset - datetime.now()).seconds + 1
                    logger.warning(f"Rate limit exceeded, waiting {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Fetch price (simulated)
                price_data = await self._fetch_from_api(symbol)
                
                # Update rate limit tracking
                self.rate_limit_remaining -= 1
                
                return {
                    "symbol": symbol,
                    "price": price_data["price"],
                    "currency": price_data["currency"],
                    "timestamp": datetime.now().isoformat(),
                    "source": price_data["source"],
                    "confidence": price_data["confidence"],
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Failed to fetch price after {max_retries} attempts: {str(e)}")
                    raise
                
                # Exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time:.2f}s: {str(e)}")
                await asyncio.sleep(wait_time)
        
        raise Exception("Max retries exceeded")
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        if datetime.now() > self.rate_limit_reset:
            self.rate_limit_remaining = 100
            self.rate_limit_reset = datetime.now() + timedelta(minutes=1)
        
        return self.rate_limit_remaining > 0
    
    async def _fetch_from_api(self, symbol: str) -> Dict[str, Any]:
        """Fetch price from simulated API with occasional failures."""
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simulate occasional API failures (5% failure rate)
        if random.random() < 0.05:
            raise Exception(f"API temporarily unavailable for {symbol}")
        
        # Simulate rate limiting (2% rate limit hits)
        if random.random() < 0.02:
            self.rate_limit_remaining = 0
            self.rate_limit_reset = datetime.now() + timedelta(seconds=30)
            raise Exception("Rate limit exceeded")
        
        # Return simulated price data
        base_prices = {
            "AAPL": 150.00,
            "GOOGL": 2500.00,
            "MSFT": 300.00,
            "AMZN": 3200.00,
            "TSLA": 200.00
        }
        
        base_price = base_prices.get(symbol, 100.00)
        fluctuated_price = base_price * random.uniform(0.98, 1.02)
        
        return {
            "price": round(fluctuated_price, 2),
            "currency": "USD",
            "source": "simulated-market-api",
            "confidence": round(random.uniform(0.85, 0.99), 2)
        }

# Example usage
async def main():
    """Example usage of the MarketPriceAgent."""
    async with MarketPriceAgent() as agent:
        try:
            result = await agent.fetch_price("AAPL")
            print(f"Price result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())