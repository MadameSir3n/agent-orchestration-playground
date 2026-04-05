import asyncio
import logging
from temporalio import workflow
from temporalio.worker import Worker
from temporalio.client import Client

# Import workflows and activities
from temporal.workflows import FinancialWorkflow, BatchProcessingWorkflow
from temporal.activities import (
    validate_input,
    fetch_market_price,
    calculate_tax,
    send_notification
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main worker service that runs the orchestration workflows."""
    
    # Connect to Temporal server
    client = await Client.connect("temporal:7233", namespace="default")
    
    # Create worker with workflows and activities
    worker = Worker(
        client,
        task_queue="financial-task-queue",
        workflows=[FinancialWorkflow, BatchProcessingWorkflow],
        activities=[
            validate_input,
            fetch_market_price,
            calculate_tax,
            send_notification
        ],
    )
    
    logger.info("Starting Temporal worker...")
    
    # Run worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())