from temporalio import workflow
from temporalio.common import RetryPolicy
from typing import List, Dict, Any
import asyncio
import logging
from datetime import timedelta

# Import activities
from .activities import (
    fetch_market_price,
    calculate_tax,
    send_notification,
    validate_input
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@workflow.defn
class FinancialWorkflow:
    @workflow.run
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main workflow that orchestrates financial operations with reliability patterns.
        """
        try:
            # Step 1: Validate input data
            logger.info("Starting input validation")
            validation_result = await workflow.execute_activity(
                validate_input,
                input_data,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=30),
                    backoff_coefficient=2.0,
                    maximum_attempts=3,
                ),
            )
            
            if not validation_result.get("is_valid", False):
                return {
                    "status": "failed",
                    "error": "Input validation failed",
                    "details": validation_result.get("errors", [])
                }
            
            # Step 2: Fetch market price with retry policy
            logger.info("Fetching market price")
            market_price = await workflow.execute_activity(
                fetch_market_price,
                input_data.get("symbol", "AAPL"),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=60),
                    backoff_coefficient=2.0,
                    maximum_attempts=5,
                ),
            )
            
            # Step 3: Calculate tax with rate limiting awareness
            logger.info("Calculating tax")
            tax_data = {
                "amount": market_price * input_data.get("quantity", 1),
                "jurisdiction": input_data.get("jurisdiction", "US-CA")
            }
            
            tax_result = await workflow.execute_activity(
                calculate_tax,
                tax_data,
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=15),
                    backoff_coefficient=1.5,
                    maximum_attempts=3,
                ),
            )
            
            # Step 4: Send notification with idempotency
            logger.info("Sending notification")
            notification_data = {
                "message": f"Trade executed: {input_data.get('symbol')} x{input_data.get('quantity')}",
                "recipient": input_data.get("recipient", "user@example.com"),
                "transaction_id": workflow.info().workflow_id
            }
            
            notification_result = await workflow.execute_activity(
                send_notification,
                notification_data,
                start_to_close_timeout=timedelta(seconds=15),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(seconds=30),
                    backoff_coefficient=2.0,
                    maximum_attempts=3,
                ),
            )
            
            # Compile final result
            result = {
                "status": "success",
                "market_price": market_price,
                "tax_amount": tax_result.get("tax_amount", 0),
                "total_cost": market_price * input_data.get("quantity", 1) + tax_result.get("tax_amount", 0),
                "notification_sent": notification_result.get("sent", False),
                "workflow_id": workflow.info().workflow_id,
                "execution_time": workflow.info().workflow_execution_timeout
            }
            
            logger.info(f"Workflow completed successfully: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "workflow_id": workflow.info().workflow_id
            }

@workflow.defn
class BatchProcessingWorkflow:
    @workflow.run
    async def run(self, batch_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of financial operations with parallel execution and error handling.
        """
        results = []
        failed_items = []
        
        # Process items in parallel with controlled concurrency
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent operations
        
        async def process_item(item):
            async with semaphore:
                try:
                    # Create a sub-workflow for each item
                    item_workflow_id = f"item-{item.get('id', 'unknown')}-{workflow.info().workflow_id}"
                    result = await workflow.execute_child_workflow(
                        FinancialWorkflow.run,
                        item,
                        id=item_workflow_id,
                        retry_policy=RetryPolicy(
                            initial_interval=timedelta(seconds=1),
                            maximum_interval=timedelta(seconds=10),
                            backoff_coefficient=2.0,
                            maximum_attempts=2,
                        ),
                    )
                    results.append(result)
                except Exception as e:
                    failed_items.append({
                        "item_id": item.get("id", "unknown"),
                        "error": str(e)
                    })
        
        # Process all items concurrently
        tasks = [process_item(item) for item in batch_data]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "status": "completed",
            "successful_items": len(results),
            "failed_items": len(failed_items),
            "results": results,
            "failures": failed_items,
            "total_processed": len(batch_data)
        }