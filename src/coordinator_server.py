import json
import time
import os
from datetime import datetime
from threading import Thread
from src.utils.network import MessageServer
from src.models.task import Task

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
            return self.register_worker(worker_id, client)
        elif action == 'heartbeat':
            return self.update_heartbeat(worker_id)
        elif action == 'get_task':
            return self.assign_task()
        elif action == 'submit_result':
            return self.submit_task_result(message)
        
        return {"status": "error", "message": "Unknown action"}
    
    def register_worker(self, worker_id, client):
        """Register a new worker"""
        if worker_id:
            self.worker_registry[worker_id] = {
                'client': client,
                'status': 'available',
                'last_heartbeat': time.time()
            }
            print(f"Registered worker {worker_id}")
            return {"status": "ok"}
        return {"status": "error", "message": "Invalid worker ID"}
    
    def update_heartbeat(self, worker_id):
        """Update worker heartbeat"""
        if worker_id in self.worker_registry:
            self.worker_registry[worker_id]['last_heartbeat'] = time.time()
            return {"status": "ok"}
        return {"status": "error", "message": "Worker not found"}
    
    def assign_task(self):
        """Assign tasks to available workers"""
        if not self.pending_tasks:
            return {"status": "ok", "has_task": False}
        
        self.pending_tasks.sort(key=lambda t: t.priority, reverse=True)
        task = self.pending_tasks.pop(0)
        self.tasks.append(task)
        
        return {"status": "ok", "has_task": True, "task": task.to_dict()}
    
    def submit_task_result(self, message):
        """Process task results from workers"""
        task_id = message.get('task_id')
        result = message.get('result')
        error = message.get('error')
        
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.update_status('failed' if error else 'completed')
            task.error = error if error else None
            task.result = result if not error else None
            
            self.completed_tasks[task.id] = task
            self.tasks.remove(task)
            
            print(f"Task {task_id} {'failed' if error else 'completed'}")
            return {"status": "ok"}
        
        return {"status": "error", "message": "Task not found"}
    
    @staticmethod
    def load_config():
        """Load configuration from settings.json file."""
        try:
            with open('config/settings.json', 'r') as config_file:
                return json.load(config_file)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return {"coordinator_host": "localhost", "coordinator_port": 5000}
    
    def save_state(self):
        """Save current state to a file for the dashboard"""
        os.makedirs('data', exist_ok=True)
        
        def serialize_tasks(task_list):
            return [task.to_dict() for task in task_list]
        
        workers = {
            worker_id: {
                'status': info.get('status', 'unknown'),
                'last_heartbeat': datetime.fromtimestamp(info.get('last_heartbeat', 0)).strftime("%Y-%m-%d %H:%M:%S")
            }
            for worker_id, info in self.worker_registry.items()
        }
        
        stats = {
            'pending': len(self.pending_tasks),
            'active': len(self.tasks),
            'completed': len([t for t in self.completed_tasks.values() if t.status == 'completed']),
            'failed': len([t for t in self.completed_tasks.values() if t.status == 'failed'])
        }
        
        state = {
            'workers': workers,
            'tasks': {
                'pending': serialize_tasks(self.pending_tasks),
                'active': serialize_tasks(self.tasks),
                'completed': serialize_tasks([t for t in self.completed_tasks.values() if t.status == 'completed']),
                'failed': serialize_tasks([t for t in self.completed_tasks.values() if t.status == 'failed'])
            },
            'stats': stats
        }
        
        with open('data/state.json', 'w') as f:
            json.dump(state, f, indent=2)


# Define handle_commands as a standalone function (not part of the class)
def handle_commands(coordinator):
    """Handle commands entered in the coordinator console"""
    print("\nCommand interface ready. Type 'help' for available commands.")
    while True:
        try:
            command = input("> ")
            if command.startswith("add "):
                parts = command.split(" ", 2)
                if len(parts) < 2:
                    print("Usage: add [url] <priority>")
                    continue
                
                url = parts[1]
                priority = int(parts[2]) if len(parts) > 2 else 5
                task_id = coordinator.add_task(url, priority)
                print(f"Added task {task_id} for URL {url} with priority {priority}")
            
            elif command == "status":
                print(f"Status: {len(coordinator.pending_tasks)} pending, "
                    f"{len(coordinator.tasks)} active, "
                    f"{len(coordinator.completed_tasks)} completed")
                
            elif command == "workers":
                for worker_id, info in coordinator.worker_registry.items():
                    last_seen = time.time() - info.get('last_heartbeat', 0)
                    print(f"Worker {worker_id}: Status={info.get('status')}, Last seen={last_seen:.1f}s ago")
                
            elif command == "help":
                print("Available commands:")
                print("  add [url] <priority> - Add a new task with optional priority (1-10)")
                print("  status - Show current status")
                print("  workers - List connected workers")
                print("  help - Show this help")
            
            else:
                print("Unknown command. Type 'help' for available commands.")
            
        except Exception as e:
            print(f"Error processing command: {e}")


# Update main function to reduce status printing frequency
def main():
    config = CoordinatorServer.load_config()
    host = config.get("coordinator_host", "localhost")
    port = config.get("coordinator_port", 5000)
    coordinator = CoordinatorServer(host=host, port=port)
    
    test_urls = [
        "https://example.com",
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://news.ycombinator.com",
        "https://github.com/trending"
    ]
    
    for url in test_urls:
        coordinator.add_task(url)
    
    print(f"Added {len(test_urls)} URLs to the task queue")
    print(f"Starting coordinator server on {host}:{port}")
    
    coordinator.start()
    Thread(target=handle_commands, args=(coordinator,), daemon=True).start()
    
    status_interval = 10  # Only print status every 10 seconds
    last_status_time = 0
    
    try:
        while True:
            time.sleep(1)
            current_time = time.time()
            
            # Save state every second but only print status every status_interval
            if current_time - last_status_time >= status_interval:
                if coordinator.tasks or coordinator.pending_tasks:
                    print(f"\nStatus update: {len(coordinator.pending_tasks)} pending, "
                          f"{len(coordinator.tasks)} active, "
                          f"{len(coordinator.completed_tasks)} completed")
                last_status_time = current_time
                
            coordinator.save_state()
    except KeyboardInterrupt:
        print("Shutting down coordinator...")
        coordinator.stop()

if __name__ == "__main__":
    main()