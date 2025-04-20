import json
import time
import uuid
import requests
from bs4 import BeautifulSoup
from src.utils.network import MessageClient

class WorkerClient:
    def __init__(self, coordinator_host, coordinator_port, user_agent, timeout):
        self.worker_id = str(uuid.uuid4())
        self.client = MessageClient(host=coordinator_host, port=coordinator_port)
        self.user_agent = user_agent
        self.timeout = timeout
        self.running = False
        
    def start(self):
        """Connect to coordinator and start processing"""
        print(f"Starting worker {self.worker_id}")
        
        # Connect to coordinator
        if not self.client.connect():
            print("Failed to connect to coordinator")
            return False
        
        # Register with coordinator
        response = self.client.send_message({
            "action": "register",
            "worker_id": self.worker_id
        })
        
        if response.get("status") != "ok":
            print("Registration failed")
            return False
               
        print("Successfully registered with coordinator")
        self.running = True
        
        # Start main processing loop
        self._process_tasks()
        
        return True
        
    def _process_tasks(self):
        """Main task processing loop"""
        while self.running:
            try:
                # Send heartbeat
                self.client.send_message({
                    "action": "heartbeat",
                    "worker_id": self.worker_id
                })
                
                # Request a task
                response = self.client.send_message({
                    "action": "get_task",
                    "worker_id": self.worker_id
                })
                
                if response.get("status") == "ok" and response.get("has_task", False):
                    task = response.get("task")
                    print(f"Received task {task['id']} for URL: {task['url']}")
                    
                    try:
                        # Process the task
                        html = self.scrape_url(task['url'])
                        result = self.process_html(html)
                        
                        # Submit result back to coordinator
                        self.client.send_message({
                            "action": "submit_result",
                            "worker_id": self.worker_id,
                            "task_id": task['id'],
                            "result": result,
                            "error": None
                        })
                        
                        print(f"Completed task {task['id']}")
                        
                    except Exception as e:
                        # Report error back to coordinator
                        print(f"Error processing task {task['id']}: {str(e)}")
                        self.client.send_message({
                            "action": "submit_result",
                            "worker_id": self.worker_id,
                            "task_id": task['id'],
                            "result": None,
                            "error": str(e)
                        })
                else:
                    # No task available, wait a bit
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error in worker loop: {str(e)}")
                time.sleep(5)  # Wait before retry on error
        
    def stop(self):
        """Stop the worker"""
        self.running = False
        self.client.disconnect()
        print("Worker stopped")
        
    def scrape_url(self, url):
        """Fetch content from URL"""
        headers = {'User-Agent': self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"HTTP error {response.status_code}")
            
    # Replace the current process_html method (around line 105-117) with this:

    def process_html(self, html):
        """Extract data from HTML content"""
        import sys
        # Increase recursion limit for complex pages
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(5000)  # Set a higher limit
    
        try:
            # Use html.parser instead of lxml for more stability
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else "No title found"
        
            # Extract limited data to avoid recursion issues
            links = len(list(soup.find_all('a', limit=1000)))
            images = len(list(soup.find_all('img', limit=500)))
        
            # Extract more data as needed
            data = {
                "title": title,
                "links": links,
                "images": images
            }
            
            return data
        finally:
            # Restore original recursion limit
            sys.setrecursionlimit(old_limit)

def load_config():
    """Load configuration from settings.json file."""
    try:
        with open('config/settings.json', 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # Provide default values if config file cannot be loaded
        return {
            "timeout": 30,
            "user_agent": "Mozilla/5.0",
            "coordinator_host": "localhost",
            "coordinator_port": 5000
        }

def main():
    # Load configuration
    config = load_config()
    
    # Create and start worker
    worker = WorkerClient(
        coordinator_host=config.get("coordinator_host", "localhost"),
        coordinator_port=config.get("coordinator_port", 5000),
        user_agent=config.get("user_agent", "Mozilla/5.0"),
        timeout=config.get("timeout", 30)
    )
    
    # Start the worker and keep running until interrupted
    if worker.start():
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down worker...")
            worker.stop()
    else:
        print("Failed to start worker")

if __name__ == "__main__":
    main()