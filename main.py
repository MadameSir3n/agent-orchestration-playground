"""
Agent Orchestration Playground
Entry point: starts the Temporal workflow worker.

Usage:
    pip install -r requirements.txt
    python main.py

    Or with Docker:
    docker-compose up
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from temporal.worker import main

if __name__ == "__main__":
    asyncio.run(main())
