import time
import logging
import gc
import psutil
import os
from threading import current_thread

logger = logging.getLogger(__name__)

class PerformanceLogger:
    def __init__(self):
        self.timers = {}
        self.metrics = {}
        self.start_memory = {}
    
    def start(self, operation_name):
        """Start timing an operation"""
        thread_id = current_thread().ident
        key = f"{operation_name}_{thread_id}"
        
        self.timers[key] = time.time()
        
        # Record memory usage at the start
        process = psutil.Process(os.getpid())
        self.start_memory[key] = process.memory_info().rss / (1024 * 1024)  # MB
        
        logger.debug(f"Started operation: {operation_name}")
    
    def end(self, operation_name):
        """End timing an operation and record metrics"""
        thread_id = current_thread().ident
        key = f"{operation_name}_{thread_id}"
        
        if key not in self.timers:
            logger.warning(f"Operation {operation_name} was never started")
            return
        
        end_time = time.time()
        duration = end_time - self.timers.pop(key)
        
        # Get memory usage at the end
        process = psutil.Process(os.getpid())
        end_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Calculate memory change
        memory_change = end_memory - self.start_memory.pop(key, 0)
        
        # Store metrics
        self.metrics[operation_name] = {
            'duration_ms': round(duration * 1000, 2),
            'memory_change_mb': round(memory_change, 2),
            'end_memory_mb': round(end_memory, 2)
        }
        
        logger.debug(f"Completed operation: {operation_name} in {duration:.2f} seconds")
        
        # Force garbage collection after operation
        gc.collect()
    
    def get_metrics(self):
        """Get all recorded metrics"""
        return self.metrics
    
    def reset(self):
        """Reset all metrics"""
        self.timers = {}
        self.metrics = {}
        self.start_memory = {}
