import json
import time
import os
from flask import Flask, render_template_string, jsonify
from datetime import datetime

app = Flask(__name__)

# Template for the dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Web Scraper Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .pending { background-color: #fff3cd; }
        .active { background-color: #cce5ff; }
        .completed { background-color: #d4edda; }
        .failed { background-color: #f8d7da; }
        .task { margin: 5px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }
        .worker { margin: 10px 0; padding: 10px; background-color: #e2e3e5; border-radius: 3px; }
        .stats { display: flex; justify-content: space-between; background-color: #f8f9fa; padding: 10px; }
        .stat { text-align: center; flex: 1; }
    </style>
</head>
<body>
    <h1>Web Scraper Dashboard</h1>
    <p>Last updated: {{ timestamp }}</p>
    
    <div class="stats">
        <div class="stat">
            <h3>Pending</h3>
            <p>{{ stats.pending }}</p>
        </div>
        <div class="stat">
            <h3>Active</h3>
            <p>{{ stats.active }}</p>
        </div>
        <div class="stat">
            <h3>Completed</h3>
            <p>{{ stats.completed }}</p>
        </div>
        <div class="stat">
            <h3>Failed</h3>
            <p>{{ stats.failed }}</p>
        </div>
    </div>
    
    <h2>Active Workers</h2>
    {% if workers %}
        {% for worker_id, info in workers.items() %}
            <div class="worker">
                <h3>Worker: {{ worker_id }}</h3>
                <p>Last heartbeat: {{ info.last_heartbeat }}</p>
                <p>Status: {{ info.status }}</p>
            </div>
        {% endfor %}
    {% else %}
        <p>No active workers</p>
    {% endif %}
    
    <h2>Tasks</h2>
    
    <h3>Pending Tasks</h3>
    <div class="status-box pending">
        {% if pending_tasks %}
            {% for task in pending_tasks %}
                <div class="task">
                    <p>ID: {{ task.id }}</p>
                    <p>URL: {{ task.url }}</p>
                    <p>Priority: {{ task.priority }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p>No pending tasks</p>
        {% endif %}
    </div>
    
    <h3>Active Tasks</h3>
    <div class="status-box active">
        {% if active_tasks %}
            {% for task in active_tasks %}
                <div class="task">
                    <p>ID: {{ task.id }}</p>
                    <p>URL: {{ task.url }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p>No active tasks</p>
        {% endif %}
    </div>
    
    <h3>Completed Tasks</h3>
    <div class="status-box completed">
        {% if completed_tasks %}
            {% for task in completed_tasks %}
                <div class="task">
                    <p>ID: {{ task.id }}</p>
                    <p>URL: {{ task.url }}</p>
                    <p>Result: {{ task.result }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p>No completed tasks</p>
        {% endif %}
    </div>
    
    <h3>Failed Tasks</h3>
    <div class="status-box failed">
        {% if failed_tasks %}
            {% for task in failed_tasks %}
                <div class="task">
                    <p>ID: {{ task.id }}</p>
                    <p>URL: {{ task.url }}</p>
                    <p>Error: {{ task.error }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p>No failed tasks</p>
        {% endif %}
    </div>
</body>
</html>
'''

def get_state_data():
    """Get the current state for the dashboard"""
    data_path = os.path.join('data', 'state.json')
    
    # Default empty state
    state = {
        "workers": {},
        "tasks": {
            "pending": [],
            "active": [],
            "completed": [],
            "failed": []
        },
        "stats": {
            "pending": 0,
            "active": 0, 
            "completed": 0,
            "failed": 0
        }
    }
    
    # Try to read the state file if it exists
    try:
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                state = json.load(f)
    except Exception as e:
        print(f"Error loading state data: {e}")
        
    return state

@app.route('/')
def dashboard():
    """Main dashboard view"""
    state = get_state_data()
    
    # Print debug info
    print("Dashboard accessed")
    print(f"State file exists: {os.path.exists('data/state.json')}")
    if os.path.exists('data/state.json'):
        print(f"State file size: {os.path.getsize('data/state.json')} bytes")
    
    return render_template_string(DASHBOARD_HTML, 
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        workers=state.get("workers", {}),
        pending_tasks=state.get("tasks", {}).get("pending", []),
        active_tasks=state.get("tasks", {}).get("active", []),
        completed_tasks=state.get("tasks", {}).get("completed", []),
        failed_tasks=state.get("tasks", {}).get("failed", []),
        stats=state.get("stats", {})
    )

@app.route('/api/state')
def api_state():
    """API endpoint to get current state"""
    return jsonify(get_state_data())

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create empty state file if it doesn't exist
    if not os.path.exists('data/state.json'):
        with open('data/state.json', 'w') as f:
            json.dump({
                "workers": {},
                "tasks": {
                    "pending": [],
                    "active": [],
                    "completed": [],
                    "failed": []
                },
                "stats": {
                    "pending": 0,
                    "active": 0, 
                    "completed": 0,
                    "failed": 0
                }
            }, f)
    
    print("Starting dashboard on http://localhost:8080")
    
    # Start the dashboard on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)