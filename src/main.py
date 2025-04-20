# filepath: /Users/chiragvijayvergiya/Desktop/chirag/dc-p/parallel-web-scraper/src/main.py
import json
import time
from src.coordinator.scheduler import Scheduler
from src.worker.scraper import Scraper

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
            "max_workers": 3
        }

def main():
    # Load configuration
    config = load_config()
    
    # Create worker pool
    workers = []
    for i in range(config.get("max_workers", 3)):
        worker = Scraper(
            user_agent=config["user_agent"],
            timeout=config["timeout"]
        )
        workers.append(worker)
        print(f"Created worker {i+1}")
    
    # Initialize the scheduler with workers
    scheduler = Scheduler(workers=workers)
    print(f"Initialized scheduler with {len(workers)} workers")

    # Add some test URLs
    test_urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://news.ycombinator.com",
        "https://github.com/trending"
    ]
    
    for url in test_urls:
        scheduler.add_task(url)
    
    print(f"Added {len(test_urls)} URLs to scrape")
    
    # Run the scheduler
    print("Starting the scraping process...")
    results = scheduler.run()
    
    # Print results
    print("\nScraping Results:")
    for task_id, task in results.items():
        if task.status == 'completed':
            print(f"Task {task_id}: {task.result.get('title', 'No title')}")
        else:
            print(f"Task {task_id}: Failed - {task.error}")

if __name__ == "__main__":
    main()