# filepath: /Users/chiragvijayvergiya/Desktop/chirag/dc-p/parallel-web-scraper/src/coordinator/scheduler.py
from src.models.task import Task
import time
import threading

class Scheduler:
    def __init__(self, workers=None):
        self.workers = workers or []
        self.tasks = []
        self.pending_tasks = []
        self.completed_tasks = {}
        self.worker_registry = {}  # Track connected workers
        self.running = True
        
    def add_task(self, url, parser=None, priority=1):
        """Add a new task to the queue"""
        task = Task(url, parser, priority)
        self.pending_tasks.append(task)
        print(f"Added task {task.id} for URL {url}")
        return task.id
        
    def schedule_task(self, url):
        """Schedule a task for a URL"""
        task_id = self.add_task(url)
        return True if task_id else False
        
    def find_available_worker(self):
        """Find an available worker to process a task"""
        for worker in self.workers:
            if worker.is_available() and worker.check_status():
                return worker
        return None
        
    def monitor_workers(self):
        """Monitor worker status"""
        active_workers = []
        for worker_id, info in self.worker_registry.items():
            if time.time() - info.get('last_heartbeat', 0) < 30:  # 30 second timeout
                active_workers.append(worker_id)
        return active_workers
        
    def run(self):
        """Run the scheduler"""
        # Move pending tasks into main task list
        self.tasks.extend(self.pending_tasks)
        self.pending_tasks = []
        
        # Process tasks in a loop
        while self.running and (self.tasks or self.pending_tasks):
            # Check for available workers
            worker = self.find_available_worker()
            
            if worker and self.tasks:
                # Get next task
                task = self.tasks.pop(0)
                
                # Assign to worker
                print(f"Assigning task {task.id} to worker")
                worker.assign_task(task)
            
            # Short sleep to avoid CPU spinning
            time.sleep(0.1)
            
        print("All tasks completed")
        return self.completed_tasks