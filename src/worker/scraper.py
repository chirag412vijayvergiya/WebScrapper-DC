# filepath: /Users/chiragvijayvergiya/Desktop/chirag/dc-p/parallel-web-scraper/src/worker/scraper.py
import requests
from bs4 import BeautifulSoup
import threading
import time

class Scraper:
    def __init__(self, user_agent, timeout):
        self.user_agent = user_agent
        self.timeout = timeout
        self.tasks = []  # Track assigned tasks
        self.max_tasks = 5  # Maximum concurrent tasks
        
    def is_available(self):
        """Check if worker can accept more tasks"""
        return len(self.tasks) < self.max_tasks
        
    def check_status(self):
        """Check if worker is operational"""
        return True
        
    def assign_task(self, task):
        """Assign a task to this worker"""
        self.tasks.append(task)
        
        # Process task in a separate thread
        thread = threading.Thread(
            target=self._process_task,
            args=(task,)
        )
        thread.daemon = True
        thread.start()
        
    def _process_task(self, task):
        """Process a single task"""
        print(f"Processing task {task.id} for URL: {task.url}")
        
        try:
            # Update task status
            task.update_status('in_progress')
            
            # Fetch the URL
            html_content = self.scrape_url(task.url)
            
            # Process the content
            result = self.process_data(html_content)
            
            # Update task with result
            task.result = result
            task.update_status('completed')
            print(f"Task {task.id} completed successfully")
            
        except Exception as e:
            # Handle errors
            print(f"Error processing task {task.id}: {str(e)}")
            task.error = str(e)
            task.update_status('failed')
            
        finally:
            # Remove task from active list
            if task in self.tasks:
                self.tasks.remove(task)
        
    def scrape_url(self, url):
        """Fetch content from a URL"""
        headers = {'User-Agent': self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to scrape {url} with status code {response.status_code}")

    def process_data(self, html_content):
        """Process the HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        
        # Extract more data as needed
        data = {
            "title": title,
            "links": len(soup.find_all('a')),
            "images": len(soup.find_all('img'))
        }
        
        return data