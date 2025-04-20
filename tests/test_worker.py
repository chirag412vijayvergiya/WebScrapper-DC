import unittest
from src.worker.scraper import Scraper

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = Scraper()

    def test_scrape_url(self):
        url = "http://example.com"
        result = self.scraper.scrape_url(url)
        self.assertIsNotNone(result)
        self.assertIn("Example Domain", result)

    def test_process_data(self):
        data = "<html><head><title>Example Domain</title></head><body></body></html>"
        processed_data = self.scraper.process_data(data)
        self.assertEqual(processed_data, {"title": "Example Domain"})  # Example expected output

if __name__ == '__main__':
    unittest.main()