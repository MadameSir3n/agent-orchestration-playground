#!/usr/bin/env python3
"""
Demo Workflows - Example usage of the agent orchestration system
"""

import asyncio
import json
from datetime import datetime
from temporalio.client import Client
from temporal.workflows import FinancialWorkflow, BatchProcessingWorkflow

async def run_single_workflow():
    """Run a single financial workflow example."""
    print("=== Single Workflow Demo ===")
    
    # Connect to Temporal
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Input data for the workflow
    input_data = {
        "symbol": "AAPL",
        "quantity": 10,
        "jurisdiction": "US-CA",
        "recipient": "trader@example.com",
        "id": "demo-001"
    }
    
    print(f"Starting workflow with input: {json.dumps(input_data, indent=2)}")
    
    # Execute the workflow
    result = await client.execute_workflow(
        FinancialWorkflow.run,
        input_data,
        id=f"financial-demo-{datetime.now().timestamp()}",
        task_queue="financial-task-queue"
    )
    
    print(f"Workflow completed: {json.dumps(result, indent=2)}")
    return result

async def run_batch_workflow():
    """Run a batch processing workflow example."""
    print("\n=== Batch Workflow Demo ===")
    
    # Connect to Temporal
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Batch of financial operations
    batch_data = [
        {
            "symbol": "AAPL",
            "quantity": 5,
            "jurisdiction": "US-CA",
            "recipient": "client1@example.com",
            "id": "batch-001"
        },
        {
            "symbol": "GOOGL",
            "quantity": 2,
            "jurisdiction": "US-NY",
            "recipient": "client2@example.com",
            "id": "batch-002"
        },
        {
            "symbol": "MSFT",
            "quantity": 15,
            "jurisdiction": "US-TX",
            "recipient": "client3@example.com",
            "id": "batch-003"
        },
        {
            "symbol": "AMZN",
            "quantity": 3,
            "jurisdiction": "EU-DE",
            "recipient": "client4@example.com",
            "id": "batch-004"
        }
    ]
    
    print(f"Starting batch workflow with {len(batch_data)} items")
    
    # Execute the batch workflow
    result = await client.execute_workflow(
        BatchProcessingWorkflow.run,
        batch_data,
        id=f"batch-demo-{datetime.now().timestamp()}",
        task_queue="financial-task-queue"
    )
    
    print(f"Batch workflow completed:")
    print(f"  Successful items: {result['successful_items']}")
    print(f"  Failed items: {result['failed_items']}")
    print(f"  Total processed: {result['total_processed']}")
    
    if result['failures']:
        print(f"  Failures: {json.dumps(result['failures'], indent=2)}")
    
    return result

async def run_error_scenario():
    """Run a workflow with intentional errors to demonstrate reliability."""
    print("\n=== Error Handling Demo ===")
    
    # Connect to Temporal
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Input data that will cause validation errors
    input_data = {
        "symbol": "INVALID",
        "quantity": -5,  # Invalid negative quantity
        "jurisdiction": "UNKNOWN",
        "recipient": "test@example.com",
        "id": "error-demo-001"
    }
    
    print(f"Starting error scenario with invalid input: {json.dumps(input_data, indent=2)}")
    
    # Execute the workflow
    result = await client.execute_workflow(
        FinancialWorkflow.run,
        input_data,
        id=f"error-demo-{datetime.now().timestamp()}",
        task_queue="financial-task-queue"
    )
    
    print(f"Error scenario result: {json.dumps(result, indent=2)}")
    return result

async def run_high_volume_scenario():
    """Run a high-volume scenario to demonstrate scalability."""
    print("\n=== High Volume Demo ===")
    
    # Connect to Temporal
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Generate 20 sample transactions
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    jurisdictions = ["US-CA", "US-NY", "US-TX", "EU-DE", "EU-FR"]
    
    batch_data = []
    for i in range(20):
        batch_data.append({
            "symbol": symbols[i % len(symbols)],
            "quantity": (i % 10) + 1,
            "jurisdiction": jurisdictions[i % len(jurisdictions)],
            "recipient": f"client{i+1}@example.com",
            "id": f"volume-{i+1:03d}"
        })
    
    print(f"Starting high volume scenario with {len(batch_data)} items")
    
    # Execute the batch workflow
    result = await client.execute_workflow(
        BatchProcessingWorkflow.run,
        batch_data,
        id=f"volume-demo-{datetime.now().timestamp()}",
        task_queue="financial-task-queue"
    )
    
    print(f"High volume scenario completed:")
    print(f"  Successful items: {result['successful_items']}")
    print(f"  Failed items: {result['failed_items']}")
    print(f"  Total processed: {result['total_processed']}")
    print(f"  Success rate: {(result['successful_items'] / result['total_processed'] * 100):.1f}%")
    
    return result

async def main():
    """Run all demo scenarios."""
    print("Agent Orchestration Playground - Demo Scenarios")
    print("=" * 50)
    
    try:
        # Run individual demos
        await run_single_workflow()
        await run_batch_workflow()
        await run_error_scenario()
        await run_high_volume_scenario()
        
        print("\n=== All demos completed successfully! ===")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        # This is expected when Temporal server isn't running
        print("Note: This demo requires the Temporal server to be running.")
        print("Start it with: docker-compose up")

if __name__ == "__main__":
    asyncio.run(main())