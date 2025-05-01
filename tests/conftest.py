import pytest
import tempfile
import os
import sys
import pathlib
import json
from datetime import datetime, timedelta
from os.path import dirname, abspath

# Add parent directory to path
parent_dir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, parent_dir)

@pytest.fixture
def temp_tasks_file():
    """Create a temporary file for tasks and clean it up after tests."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    yield temp_path
    
    # Clean up after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def sample_tasks():
    """Provide a sample set of tasks for testing."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    return [
        {
            "id": 1,
            "title": "Finish report",
            "description": "Complete quarterly report for management",
            "priority": "High",
            "category": "Work",
            "due_date": yesterday,
            "completed": False,
            "created_at": "2025-04-28 09:00:00"
        },
        {
            "id": 2,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread, and vegetables",
            "priority": "Medium",
            "category": "Personal",
            "due_date": today,
            "completed": True,
            "created_at": "2025-04-29 10:30:00"
        },
        {
            "id": 3,
            "title": "Study for exam",
            "description": "Review chapters 5-8 for tomorrow's test",
            "priority": "High",
            "category": "School",
            "due_date": today,
            "completed": False,
            "created_at": "2025-04-29 15:45:00"
        },
        {
            "id": 4,
            "title": "Call dentist",
            "description": "Schedule annual checkup appointment",
            "priority": "Low",
            "category": "Personal",
            "due_date": tomorrow,
            "completed": False,
            "created_at": "2025-04-30 08:15:00"
        },
        {
            "id": 5,
            "title": "Team meeting",
            "description": "Weekly sprint planning",
            "priority": "Medium",
            "category": "Work",
            "due_date": tomorrow,
            "completed": False,
            "created_at": "2025-04-30 09:00:00"
        }
    ]

@pytest.fixture
def tasks_file_with_data(temp_tasks_file, sample_tasks):
    """Create a temporary file with sample tasks data."""
    with open(temp_tasks_file, 'w') as f:
        json.dump(sample_tasks, f)
    
    return temp_tasks_file