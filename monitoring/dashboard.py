#!/usr/bin/env python3
"""
Monitoring Dashboard - Visualization for agent orchestration workflows
"""

from flask import Flask, render_template, jsonify, request
import pymongo
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# MongoDB connection (simulated)
class MockMongoDB:
    """Mock MongoDB for demonstration purposes."""
    
    def __init__(self):
        self.workflows = []
        self.notifications = []
        self.metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_duration": 0,
            "retry_count": 0
        }
        self._populate_mock_data()
    
    def _populate_mock_data(self):
        """Populate with mock workflow data."""
        import random
        from datetime import datetime, timedelta
        
        # Generate mock workflows
        for i in range(50):
            start_time = datetime.now() - timedelta(minutes=random.randint(1, 120))
            duration = random.uniform(5, 60)  # 5-60 seconds
            status = random.choices(["success", "failed"], weights=[0.85, 0.15])[0]
            
            workflow = {
                "id": f"wf-{i:03d}",
                "start_time": start_time.isoformat(),
                "duration": round(duration, 2),
                "status": status,
                "retries": random.randint(0, 3),
                "agent_sequence": ["market_price", "tax_calculation", "notification"]
            }
            
            self.workflows.append(workflow)
            
            # Update metrics
            self.metrics["total_workflows"] += 1
            if status == "success":
                self.metrics["successful_workflows"] += 1
            else:
                self.metrics["failed_workflows"] += 1
            self.metrics["retry_count"] += workflow["retries"]
        
        self.metrics["average_duration"] = round(
            sum(w["duration"] for w in self.workflows) / len(self.workflows), 2
        ) if self.workflows else 0

# Initialize mock database
db = MockMongoDB()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Get current system metrics."""
    return jsonify(db.metrics)

@app.route('/api/workflows')
def get_workflows():
    """Get recent workflows."""
    # Sort by start time and limit to 20 most recent
    sorted_workflows = sorted(
        db.workflows, 
        key=lambda x: x["start_time"], 
        reverse=True
    )[:20]
    
    return jsonify(sorted_workflows)

@app.route('/api/workflows/<workflow_id>')
def get_workflow_detail(workflow_id):
    """Get detailed information for a specific workflow."""
    workflow = next((w for w in db.workflows if w["id"] == workflow_id), None)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404
    
    return jsonify(workflow)

@app.route('/api/notifications')
def get_notifications():
    """Get recent notifications."""
    # Mock notification data
    notifications = [
        {
            "id": f"notif-{i:03d}",
            "timestamp": (datetime.now() - timedelta(minutes=i*2)).isoformat(),
            "recipient": f"user{i}@example.com",
            "message": f"Trade executed successfully - Attempt {i%3 + 1}",
            "status": random.choice(["delivered", "pending", "failed"]),
            "channel": random.choice(["email", "sms", "push"])
        }
        for i in range(10)
    ]
    
    return jsonify(notifications)

@app.route('/api/alerts')
def get_alerts():
    """Get current system alerts."""
    alerts = [
        {
            "id": "alert-001",
            "level": "warning",
            "message": "High retry rate detected (2.3 avg)",
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()
        },
        {
            "id": "alert-002", 
            "level": "info",
            "message": "New workflow version deployed",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
        }
    ]
    
    return jsonify(alerts)

@app.route('/api/system-health')
def get_system_health():
    """Get system health status."""
    success_rate = (
        db.metrics["successful_workflows"] / 
        max(db.metrics["total_workflows"], 1)
    ) * 100
    
    health_status = "healthy" if success_rate > 95 else "degraded" if success_rate > 90 else "unhealthy"
    
    return jsonify({
        "status": health_status,
        "uptime": "99.9%",  # Mock uptime
        "success_rate": round(success_rate, 2),
        "latency_avg": f"{db.metrics['average_duration']}s",
        "active_workflows": 5,  # Mock active count
        "last_updated": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)