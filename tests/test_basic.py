import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
import sys
import pathlib
from os.path import dirname, abspath

# Add parent directory to path to import tasks module
parent_dir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, parent_dir)

from tasks import (
    load_tasks,
    save_tasks,
    generate_unique_id,
    filter_tasks_by_priority,
    filter_tasks_by_category,
    filter_tasks_by_completion,
    search_tasks,
    get_overdue_tasks
)

"""
Unit Tests for Tasks Module

This file contains unit tests for the core functionality of the tasks module.
The tests are designed to verify each function works correctly in isolation.
"""

def test_generate_unique_id():
    """Test that generate_unique_id produces unique IDs correctly."""
    # Empty list should return ID 1
    assert generate_unique_id([]) == 1
    
    # List with tasks should return max ID + 1
    tasks = [{"id": 5}, {"id": 10}, {"id": 3}]
    assert generate_unique_id(tasks) == 11

def test_save_and_load_tasks():
    """Test saving and loading tasks to/from a JSON file."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Sample tasks data
        tasks = [
            {
                "id": 1,
                "title": "Test Task",
                "description": "Description",
                "priority": "High",
                "category": "Work",
                "due_date": "2025-05-01",
                "completed": False,
                "created_at": "2025-04-30 12:00:00"
            }
        ]
        
        # Save tasks to the temp file
        save_tasks(tasks, temp_path)
        
        # Load tasks from the temp file
        loaded_tasks = load_tasks(temp_path)
        
        # Verify the loaded data matches the original
        assert loaded_tasks == tasks
        
        # Test loading from non-existent file
        non_existent_path = temp_path + ".nonexistent"
        assert load_tasks(non_existent_path) == []
        
        # Test loading from corrupted JSON file
        with open(temp_path, "w") as f:
            f.write("This is not valid JSON")
        
        # This should return an empty list and print a warning
        assert load_tasks(temp_path) == []
        
    finally:
        # Clean up the temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_filter_tasks_by_priority():
    """Test filtering tasks by priority level."""
    tasks = [
        {"id": 1, "title": "Task 1", "priority": "High"},
        {"id": 2, "title": "Task 2", "priority": "Medium"},
        {"id": 3, "title": "Task 3", "priority": "Low"},
        {"id": 4, "title": "Task 4", "priority": "High"}
    ]
    
    # Filter for High priority
    high_priority = filter_tasks_by_priority(tasks, "High")
    assert len(high_priority) == 2
    assert all(task["priority"] == "High" for task in high_priority)
    
    # Filter for Medium priority
    medium_priority = filter_tasks_by_priority(tasks, "Medium")
    assert len(medium_priority) == 1
    assert medium_priority[0]["priority"] == "Medium"
    
    # Filter for non-existent priority
    none_priority = filter_tasks_by_priority(tasks, "Critical")
    assert len(none_priority) == 0

def test_filter_tasks_by_category():
    """Test filtering tasks by category."""
    tasks = [
        {"id": 1, "title": "Task 1", "category": "Work"},
        {"id": 2, "title": "Task 2", "category": "Personal"},
        {"id": 3, "title": "Task 3", "category": "School"},
        {"id": 4, "title": "Task 4", "category": "Work"}
    ]
    
    # Filter for Work category
    work_tasks = filter_tasks_by_category(tasks, "Work")
    assert len(work_tasks) == 2
    assert all(task["category"] == "Work" for task in work_tasks)
    
    # Filter for School category
    school_tasks = filter_tasks_by_category(tasks, "School")
    assert len(school_tasks) == 1
    assert school_tasks[0]["category"] == "School"
    
    # Filter for non-existent category
    none_category = filter_tasks_by_category(tasks, "Health")
    assert len(none_category) == 0

def test_filter_tasks_by_completion():
    """Test filtering tasks by completion status."""
    tasks = [
        {"id": 1, "title": "Task 1", "completed": True},
        {"id": 2, "title": "Task 2", "completed": False},
        {"id": 3, "title": "Task 3", "completed": True},
        {"id": 4, "title": "Task 4", "completed": False}
    ]
    
    # Filter for completed tasks
    completed = filter_tasks_by_completion(tasks, True)
    assert len(completed) == 2
    assert all(task["completed"] for task in completed)
    
    # Filter for incomplete tasks
    incomplete = filter_tasks_by_completion(tasks, False)
    assert len(incomplete) == 2
    assert all(not task["completed"] for task in incomplete)
    
    # Test with missing completion field
    tasks_missing_field = [
        {"id": 1, "title": "Task 1"},
        {"id": 2, "title": "Task 2", "completed": True}
    ]
    completed_with_missing = filter_tasks_by_completion(tasks_missing_field, True)
    assert len(completed_with_missing) == 1
    
    # Test the default parameter (completed=True)
    default_completed = filter_tasks_by_completion(tasks)
    assert len(default_completed) == 2
    assert all(task["completed"] for task in default_completed)

def test_search_tasks():
    """Test searching tasks by query text."""
    tasks = [
        {"id": 1, "title": "Complete project", "description": "Finish the Python project"},
        {"id": 2, "title": "Buy groceries", "description": "Milk, eggs, bread"},
        {"id": 3, "title": "Call doctor", "description": "Schedule annual checkup"},
        {"id": 4, "title": "Project review", "description": "Review team's progress"}
    ]
    
    # Search in titles
    project_tasks = search_tasks(tasks, "project")
    assert len(project_tasks) == 2
    
    # Search in descriptions
    python_tasks = search_tasks(tasks, "python")
    assert len(python_tasks) == 1
    assert python_tasks[0]["id"] == 1
    
    # Case insensitive search
    case_tasks = search_tasks(tasks, "PYTHON")
    assert len(case_tasks) == 1
    
    # No matches
    no_matches = search_tasks(tasks, "vacation")
    assert len(no_matches) == 0
    
    # Test with missing fields
    tasks_missing_fields = [
        {"id": 1},
        {"id": 2, "title": "Test"},
        {"id": 3, "description": "test content"}
    ]
    results_in_title = search_tasks(tasks_missing_fields, "test")
    assert len(results_in_title) == 2
    assert results_in_title[0]["id"] == 2
    
    results_in_desc = search_tasks(tasks_missing_fields, "content")
    assert len(results_in_desc) == 1
    assert results_in_desc[0]["id"] == 3

def test_get_overdue_tasks():
    """Test identifying overdue tasks."""
    # Use timedelta instead of manual day adjustment to avoid month boundary issues
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    tasks = [
        {"id": 1, "title": "Overdue task", "due_date": yesterday_str, "completed": False},
        {"id": 2, "title": "Future task", "due_date": tomorrow_str, "completed": False},
        {"id": 3, "title": "Completed overdue", "due_date": yesterday_str, "completed": True},
        {"id": 4, "title": "No due date", "completed": False},
        {"id": 5, "title": "Empty due date", "due_date": "", "completed": False},
        {"id": 6, "title": "Invalid due date", "due_date": "not-a-date", "completed": False}
    ]
    
    overdue = get_overdue_tasks(tasks)
    # Only task 1 should be overdue - a task that has a due date in the past and is not completed
    assert len(overdue) == 1
    assert overdue[0]["id"] == 1
    
    # Test with an empty task list
    assert get_overdue_tasks([]) == []

if __name__ == "__main__":
    pytest.main(["-v", __file__])