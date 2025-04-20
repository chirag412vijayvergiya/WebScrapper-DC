# Parallel Web Scraper

## Overview
The Parallel Web Scraper is a distributed web scraping application designed to efficiently collect data from multiple websites by utilizing multiple machines. This project is structured to separate the responsibilities of coordinating tasks and executing scraping operations, allowing for scalable and efficient data collection.

## Architecture
The architecture of the Parallel Web Scraper consists of the following components:

- **Coordinator**: Manages the distribution of scraping tasks to worker nodes. It schedules tasks and monitors the status of workers.
- **Worker**: Executes the scraping tasks assigned by the coordinator. Each worker scrapes data from specified URLs and processes the collected data.
- **Models**: Defines the data structures used in the application, such as tasks representing individual scraping operations.
- **Utils**: Contains utility functions for network operations, facilitating communication between the coordinator and workers.

## Project Structure
```
parallel-web-scraper
├── src
│   ├── main.py               # Entry point of the application
│   ├── coordinator           # Coordinator component
│   │   ├── __init__.py
│   │   └── scheduler.py      # Task scheduling and worker monitoring
│   ├── worker                # Worker component
│   │   ├── __init__.py
│   │   └── scraper.py        # Web scraping logic
│   ├── models                # Data models
│   │   ├── __init__.py
│   │   └── task.py           # Task representation
│   └── utils                 # Utility functions
│       ├── __init__.py
│       └── network.py        # Network operations
├── config
│   └── settings.json         # Configuration settings
├── tests                     # Unit tests
│   ├── test_coordinator.py
│   └── test_worker.py
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/parallel-web-scraper.git
   cd parallel-web-scraper
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the settings in `config/settings.json` as needed.

4. Run the application:
   ```
   python src/main.py
   ```

## Usage
- The coordinator will distribute scraping tasks to available workers.
- Workers will scrape data from the assigned URLs and return the results to the coordinator.
- Monitor the output for progress and results.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.# WebScrapper-DC
