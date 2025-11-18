"""
Performance monitoring utilities
"""

import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


def timeit(operation_name: str) -> Callable:
    """
    Decorator to measure execution time of async/sync functions.

    Args:
        operation_name: Name of the operation being timed

    Returns:
        Decorated function that logs execution time
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"{operation_name} completed in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{operation_name} failed after {elapsed:.2f}s: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"{operation_name} completed in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{operation_name} failed after {elapsed:.2f}s: {e}")
                raise

        # Detect if function is async
        import asyncio
        import inspect

        try:
            if asyncio.iscoroutinefunction(func) or inspect.iscoroutinefunction(func):
                return async_wrapper  # type: ignore
        except Exception as e:
            # Log initialization failure but don't break the application
            logger.warning(
                "Performance monitoring initialization failed for %s: %s",
                operation_name,
                e,
            )

        return sync_wrapper  # type: ignore

    return decorator
