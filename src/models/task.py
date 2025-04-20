import uuid
from datetime import datetime

class Task:
    def __init__(self, url, parser=None, priority=1):
        self.id = str(uuid.uuid4())
        self.url = url
        self.parser = parser  # Function to extract specific data
        self.priority = priority
        self.status = 'pending'  # pending, in_progress, completed, failed
        self.created_at = datetime.now()
        self.completed_at = None
        self.result = None
        self.error = None
        self.assigned_worker = None

    def execute(self):
        # Logic to perform the scraping task
        self.update_status('in_progress')
        # Actual execution will be handled by the worker
        
    def update_status(self, new_status):
        self.status = new_status
        if new_status in ['completed', 'failed']:
            self.completed_at = datetime.now()
            
    def to_dict(self):
        """Convert task to dictionary for serialization"""
        return {
            'id': self.id,
            'url': self.url,
            'priority': self.priority,
            'status': self.status,
            'created_at': str(self.created_at),
            'completed_at': str(self.completed_at) if self.completed_at else None,
            'result': self.result,
            'error': self.error,
            'assigned_worker': self.assigned_worker
        }