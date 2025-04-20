import unittest
from src.coordinator.scheduler import Scheduler
from unittest.mock import patch, MagicMock

class TestScheduler(unittest.TestCase):

    @patch('src.coordinator.scheduler.Scheduler.schedule_task')
    def test_schedule_task(self, mock_schedule_task):
        scheduler = Scheduler()
        mock_schedule_task.return_value = True
        
        result = scheduler.schedule_task('http://example.com')
        
        self.assertTrue(result)
        mock_schedule_task.assert_called_once_with('http://example.com')

    @patch('src.coordinator.scheduler.Scheduler.monitor_workers')
    def test_monitor_workers(self, mock_monitor_workers):
        scheduler = Scheduler()
        mock_monitor_workers.return_value = ['worker1', 'worker2']
        
        result = scheduler.monitor_workers()
        
        self.assertEqual(result, ['worker1', 'worker2'])
        mock_monitor_workers.assert_called_once()

if __name__ == '__main__':
    unittest.main()