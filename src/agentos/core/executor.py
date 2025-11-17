from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import structlog

logger = structlog.get_logger()

@dataclass
class ExecutionResult:
    """Result of task execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    duration_seconds: float = 0.0
    steps_completed: int = 0

class TaskExecutor:
    """
    Execute multi-step tasks with error handling.
    
    Features:
    - Step-by-step execution
    - Error recovery
    - Progress tracking
    - Result aggregation
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        print(f"[DEBUG] TaskExecutor initialized - Max retries: {max_retries}")
    
    async def execute_task(
        self,
        steps: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a multi-step task.
        
        Args:
            steps: List of step definitions
            context: Shared context across steps
        
        Returns:
            ExecutionResult with aggregated results
        """
        print(f"[DEBUG] Starting task execution - Total steps: {len(steps)}")
        start_time = datetime.now()
        results = []
        context = context or {}
        
        for i, step in enumerate(steps):
            print(f"[DEBUG] Executing step {i+1}/{len(steps)}")
            logger.info("executing_step", step_num=i+1, total=len(steps))
            
            try:
                result = await self._execute_step(step, context)
                results.append(result)
                
                if not result["success"]:
                    print(f"[DEBUG ERROR] Step {i+1} failed - Error: {result.get('error')}")
                    logger.error("step_failed", step_num=i+1)
                    return ExecutionResult(
                        success=False,
                        output=results,
                        error=f"Step {i+1} failed: {result.get('error')}",
                        duration_seconds=(datetime.now() - start_time).total_seconds(),
                        steps_completed=i
                    )
                
                print(f"[DEBUG] Step {i+1} completed successfully")
                # Update shared context
                if "output" in result:
                    context[f"step_{i}_output"] = result["output"]
                
            except Exception as e:
                print(f"[DEBUG ERROR] Step {i+1} exception - Error: {str(e)}")
                logger.error("step_exception", step_num=i+1, error=str(e))
                return ExecutionResult(
                    success=False,
                    output=results,
                    error=str(e),
                    duration_seconds=(datetime.now() - start_time).total_seconds(),
                    steps_completed=i
                )
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"[DEBUG] Task execution completed successfully - Duration: {duration}s, Steps: {len(steps)}")
        
        return ExecutionResult(
            success=True,
            output=results,
            duration_seconds=duration,
            steps_completed=len(steps)
        )
    
    async def _execute_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single step with retry logic."""
        tool_name = step.get("tool")
        arguments = step.get("arguments", {})
        print(f"[DEBUG] Executing step with tool - Tool: {tool_name}, Args: {arguments}")
        
        for attempt in range(self.max_retries):
            try:
                print(f"[DEBUG] Attempt {attempt+1}/{self.max_retries} for {tool_name}")
                # This would call the actual tool executor
                # For now, placeholder
                await asyncio.sleep(0.1)  # Simulate work
                
                print(f"[DEBUG] Step execution successful on attempt {attempt+1}")
                return {
                    "success": True,
                    "output": f"Executed {tool_name}",
                }
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"[DEBUG ERROR] Max retries exceeded for {tool_name}")
                    raise
                print(f"[DEBUG] Retry {attempt+1} - Error: {str(e)}")
                logger.warning("step_retry", attempt=attempt+1, error=str(e))
                await asyncio.sleep(1)
        
        print(f"[DEBUG ERROR] Step execution failed after {self.max_retries} attempts")
        return {"success": False, "error": "Max retries exceeded"}
