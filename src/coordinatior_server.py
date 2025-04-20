import json
import time
from src.utils.network import MessageServer
from src.models.task import Task
import os
from datetime import datetime

class CoordinatorServer(MessageServer):
    def __init__(self, host='localhost', port=5000):
        super().__init__(host=host, port=port)
        self.tasks = []
        self.pending_tasks = []
        self.completed_tasks = {}
        self.worker_registry = {}
        
    def add_task(self, url, priority=1):
        """Add a new task to the queue"""
        task = Task(url, priority=priority)
        self.pending_tasks.append(task)
        print(f"Added task {task.id} for URL {url}")
        return task.id
        
    def process_message(self, message, client):
        """Handle messages from workers"""
        if 'action' not in message:
            return {"status": "error", "message": "Invalid message format"}
               
        action = message.get('action')
        worker_id = message.get('worker_id')
        
        if action == 'register':
            # Register a new worker
            if worker_id:
                self.worker_registry[worker_id] = {
                    'client': client,
                    'status': 'available',
                    'last_heartbeat': time.time()
                }
                print(f"Registered worker {worker_id}")
                return {"status": "ok"}
        
        elif action == 'heartbeat':
            # Update worker heartbeat
            if worker_id in self.worker_registry:
                self.worker_registry[worker_id]['last_heartbeat'] = time.time()
                return {"status": "ok"}
        
        elif action == 'get_task':
            # Worker requesting a task
            if not self.pending_tasks:
                return {"status": "ok", "has_task": False}
                
            # Sort tasks by priority
            self.pending_tasks.sort(key=lambda t: t.priority, reverse=True)
            task = self.pending_tasks.pop(0)
            
            # Move to active tasks
            self.tasks.append(task)
            
            # Return task to worker
            return {
                "status": "ok", 
                "has_task": True,
                "task": task.to_dict()
            }
            
        elif action == 'submit_result':
            # Worker submitting a task result
            task_id = message.get('task_id')
            result = message.get('result')
            error = message.get('error')
            
            # Find the task
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                if error:
                    task.update_status('failed')
                    task.error = error
                else:
                    task.update_status('completed')
                    task.result = result
                    
                # Move to completed tasks
                self.completed_tasks[task.id] = task
                self.tasks.remove(task)
                
                print(f"Task {task_id} {'completed' if not error else 'failed'}")
                return {"status": "ok"}
            else:
                return {"status": "error", "message": "Task not found"}
        
        return {"status": "error", "message": "Unknown action"}
    
    # Add this method to the CoordinatorServer class
def save_state(self):
    """Save current state to a file for the dashboard"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Convert tasks to serializable format
    pending_tasks = []
    for task in self.pending_tasks:
        task_dict = task.to_dict()
        pending_tasks.append(task_dict)
    
    active_tasks = []
    for task in self.tasks:
        task_dict = task.to_dict()
        active_tasks.append(task_dict)
    
    completed_tasks = []
    failed_tasks = []
    
    for task_id, task in self.completed_tasks.items():
        task_dict = task.to_dict()
        if task.status == 'completed':
            completed_tasks.append(task_dict)
        elif task.status == 'failed':
            failed_tasks.append(task_dict)
    
    # Convert worker registry to serializable format
    workers = {}
    for worker_id, info in self.worker_registry.items():
        workers[worker_id] = {
            'status': info.get('status', 'unknown'),
            'last_heartbeat': datetime.fromtimestamp(info.get('last_heartbeat', 0)).strftime("%Y-%m-%d %H:%M:%S"),
            'current_task': None  # Add logic to track current task if needed
        }
    
    # Compile stats
    stats = {
        'pending': len(self.pending_tasks),
        'active': len(self.tasks),
        'completed': len([t for t in self.completed_tasks.values() if t.status == 'completed']),
        'failed': len([t for t in self.completed_tasks.values() if t.status == 'failed'])
    }
    
    # Create state object
    state = {
        'workers': workers,
        'tasks': {
            'pending': pending_tasks,
            'active': active_tasks,
            'completed': completed_tasks,
            'failed': failed_tasks
        },
        'stats': stats
    }
    
    # Write to file
    try:
        with open('data/state.json', 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def load_config():
    """Load configuration from settings.json file."""
    try:
        with open('config/settings.json', 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {
            "coordinator_host": "localhost",
            "coordinator_port": 5000
        }

def main():
    # Load configuration
    config = load_config()
    
    # Create and start the coordinator server
    host = config.get("coordinator_host", "localhost")
    port = config.get("coordinator_port", 5000)
    coordinator = CoordinatorServer(host=host, port=port)
    
    # Add some example URLs to scrape
    test_urls = [
        "https://example.com",
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://news.ycombinator.com",
        "https://github.com/trending",
    ]
    
    for url in test_urls:
        coordinator.add_task(url)
        
    print(f"Added {len(test_urls)} URLs to the task queue")
    print(f"Starting coordinator server on {host}:{port}")
    
    # Start the server
    coordinator.start()
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
        
            # Print periodic status updates
            if coordinator.tasks or coordinator.pending_tasks:
                print(f"Status: {len(coordinator.pending_tasks)} pending, "
                        f"{len(coordinator.tasks)} active, "
                        f"{len(coordinator.completed_tasks)} completed")
        
        # Save state for dashboard
            coordinator.save_state()
            
    except KeyboardInterrupt:
        print("Shutting down coordinator...")
        coordinator.stop()

if __name__ == "__main__":
    main()