import unittest
import os
import json
from datetime import datetime, timedelta
import tasks

class TestTDDFeatures(unittest.TestCase):
    """Test class for implementing new features using TDD."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Use a test file to avoid affecting real data
        self.test_file = "test_tasks.json"
        
        # Sample tasks for testing
        self.sample_tasks = [
            {
                "id": 1,
                "title": "Complete project report",
                "description": "Finish the quarterly report",
                "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "priority": "High",
                "category": "Work",
                "completed": False
            },
            {
                "id": 2,
                "title": "Buy groceries",
                "description": "Get milk, eggs, and bread",
                "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "priority": "Medium",
                "category": "Personal",
                "completed": False
            },
            {
                "id": 3,
                "title": "Call doctor",
                "description": "Schedule annual checkup",
                "due_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "priority": "High",
                "category": "Health",
                "completed": True
            }
        ]
        
        # Save sample tasks to test file
        with open(self.test_file, "w") as f:
            json.dump(self.sample_tasks, f)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # Feature 1: Task Tagging System
    def test_add_tags_to_task(self):
        """Test adding tags to a task."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Add tags to task with ID 1
        task_id = 1
        tags = ["urgent", "Q4", "presentation"]
        
        # This should fail initially as the add_tags_to_task function doesn't exist yet
        tasks.add_tags_to_task(task_data, task_id, tags, self.test_file)
        
        # Reload tasks to verify changes were saved
        updated_tasks = tasks.load_tasks(self.test_file)
        
        # Find the task with ID 1
        task = next((t for t in updated_tasks if t["id"] == task_id), None)
        
        # Assert task has tags field with the tags we added
        self.assertIsNotNone(task)
        self.assertIn("tags", task)
        self.assertEqual(set(task["tags"]), set(tags))

    def test_remove_tag_from_task(self):
        """Test removing a tag from a task."""
        # First add tags to a task
        task_data = tasks.load_tasks(self.test_file)
        task_id = 2
        initial_tags = ["shopping", "errand", "weekly"]
        
        # Add initial tags first
        tasks.add_tags_to_task(task_data, task_id, initial_tags, self.test_file)
        
        # Now remove a specific tag
        tag_to_remove = "errand"
        tasks.remove_tag_from_task(task_data, task_id, tag_to_remove, self.test_file)
        
        # Reload tasks to verify changes
        updated_tasks = tasks.load_tasks(self.test_file)
        task = next((t for t in updated_tasks if t["id"] == task_id), None)
        
        # Assert the tag was removed
        self.assertIsNotNone(task)
        self.assertIn("tags", task)
        self.assertNotIn(tag_to_remove, task["tags"])
        # The other tags should still be there
        self.assertIn("shopping", task["tags"])
        self.assertIn("weekly", task["tags"])

    def test_filter_tasks_by_tag(self):
        """Test filtering tasks by tag."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Add tags to multiple tasks
        tasks.add_tags_to_task(task_data, 1, ["urgent", "report", "Q4"], self.test_file)
        tasks.add_tags_to_task(task_data, 2, ["shopping", "errand"], self.test_file)
        tasks.add_tags_to_task(task_data, 3, ["health", "appointment", "urgent"], self.test_file)
        
        # Filter tasks by the "urgent" tag
        urgent_tasks = tasks.filter_tasks_by_tag(task_data, "urgent")
        
        # Should return tasks with IDs 1 and 3
        self.assertEqual(len(urgent_tasks), 2)
        task_ids = [task["id"] for task in urgent_tasks]
        self.assertIn(1, task_ids)
        self.assertIn(3, task_ids)
        
        # Filter by a tag that only one task has
        report_tasks = tasks.filter_tasks_by_tag(task_data, "report")
        self.assertEqual(len(report_tasks), 1)
        self.assertEqual(report_tasks[0]["id"], 1)
        
        # Filter by a non-existent tag
        no_tasks = tasks.filter_tasks_by_tag(task_data, "nonexistent")
        self.assertEqual(len(no_tasks), 0)

    # Feature 2: Task Sorting
    def test_sort_tasks_by_due_date(self):
        """Test sorting tasks by due date."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Sort tasks by due date (ascending)
        sorted_tasks = tasks.sort_tasks(task_data, "due_date", ascending=True)
        
        # Check that tasks are sorted by due date
        for i in range(len(sorted_tasks) - 1):
            if sorted_tasks[i].get("due_date") and sorted_tasks[i+1].get("due_date"):
                self.assertLessEqual(sorted_tasks[i]["due_date"], sorted_tasks[i+1]["due_date"])
        
        # Also test descending order
        sorted_tasks_desc = tasks.sort_tasks(task_data, "due_date", ascending=False)
        for i in range(len(sorted_tasks_desc) - 1):
            if sorted_tasks_desc[i].get("due_date") and sorted_tasks_desc[i+1].get("due_date"):
                self.assertGreaterEqual(sorted_tasks_desc[i]["due_date"], sorted_tasks_desc[i+1]["due_date"])

    def test_sort_tasks_by_priority(self):
        """Test sorting tasks by priority."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Define priority order: High > Medium > Low
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        
        # Sort tasks by priority (descending)
        sorted_tasks = tasks.sort_tasks(task_data, "priority", ascending=False)
        
        # Check that tasks are sorted by priority
        for i in range(len(sorted_tasks) - 1):
            if sorted_tasks[i].get("priority") and sorted_tasks[i+1].get("priority"):
                # Convert priority to numeric value for comparison
                priority1 = priority_order.get(sorted_tasks[i]["priority"], 0)
                priority2 = priority_order.get(sorted_tasks[i+1]["priority"], 0)
                self.assertGreaterEqual(priority1, priority2)

    def test_sort_tasks_by_title(self):
        """Test sorting tasks by title."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Sort tasks alphabetically by title
        sorted_tasks = tasks.sort_tasks(task_data, "title", ascending=True)
        
        # Check that tasks are sorted alphabetically
        for i in range(len(sorted_tasks) - 1):
            if sorted_tasks[i].get("title") and sorted_tasks[i+1].get("title"):
                self.assertLessEqual(sorted_tasks[i]["title"].lower(), sorted_tasks[i+1]["title"].lower())

    # Feature 3: Recurring Tasks
    def test_create_recurring_task(self):
        """Test creating a recurring task."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Create a recurring task
        recurring_task = {
            "title": "Weekly team meeting",
            "description": "Regular team sync-up",
            "category": "Work",
            "priority": "Medium",
            "recurrence": {
                "pattern": "weekly",
                "interval": 1,  # every 1 week
                "end_after": 10  # ends after 10 occurrences
            }
        }
        
        # Add the recurring task
        new_task_id = tasks.add_recurring_task(task_data, recurring_task, self.test_file)
        
        # Reload tasks to verify changes
        updated_tasks = tasks.load_tasks(self.test_file)
        new_task = next((t for t in updated_tasks if t["id"] == new_task_id), None)
        
        # Assert the task was added and has recurrence info
        self.assertIsNotNone(new_task)
        self.assertIn("recurrence", new_task)
        self.assertEqual(new_task["recurrence"]["pattern"], "weekly")
        self.assertEqual(new_task["recurrence"]["interval"], 1)
        self.assertEqual(new_task["recurrence"]["end_after"], 10)

    def test_generate_next_occurrence(self):
        """Test generating the next occurrence of a recurring task."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Create a daily recurring task
        recurring_task = {
            "title": "Daily review",
            "description": "Review daily tasks",
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "category": "Work",
            "priority": "Medium",
            "completed": False,
            "recurrence": {
                "pattern": "daily",
                "interval": 1  # every day
            }
        }
        
        # Add the recurring task
        task_id = tasks.add_recurring_task(task_data, recurring_task, self.test_file)
        
        # Generate the next occurrence after marking as complete
        tasks.complete_task(task_data, task_id, self.test_file)
        next_occurrence = tasks.generate_next_occurrence(task_data, task_id, self.test_file)
        
        # Reload tasks to verify
        updated_tasks = tasks.load_tasks(self.test_file)
        
        # The original task should be marked complete
        original_task = next((t for t in updated_tasks if t["id"] == task_id), None)
        self.assertIsNotNone(original_task)
        self.assertTrue(original_task["completed"])
        
        # A new task should be created for the next occurrence
        next_task = next((t for t in updated_tasks if t["id"] == next_occurrence), None)
        self.assertIsNotNone(next_task)
        self.assertFalse(next_task["completed"])
        
        # The due date should be 1 day later
        original_date = datetime.strptime(original_task["due_date"], "%Y-%m-%d")
        next_date = datetime.strptime(next_task["due_date"], "%Y-%m-%d")
        self.assertEqual(next_date, original_date + timedelta(days=1))

    def test_list_recurring_tasks(self):
        """Test listing all recurring tasks."""
        task_data = tasks.load_tasks(self.test_file)
        
        # Add multiple recurring tasks
        recurring_task1 = {
            "title": "Weekly meeting",
            "recurrence": {"pattern": "weekly", "interval": 1}
        }
        recurring_task2 = {
            "title": "Monthly report",
            "recurrence": {"pattern": "monthly", "interval": 1}
        }
        
        tasks.add_recurring_task(task_data, recurring_task1, self.test_file)
        tasks.add_recurring_task(task_data, recurring_task2, self.test_file)
        
        # Also add a non-recurring task to make sure it's not included
        non_recurring = {"title": "One-time task"}
        tasks.add_task(task_data, non_recurring, self.test_file)
        
        # List all recurring tasks
        recurring_tasks = tasks.list_recurring_tasks(task_data)
        
        # Should have at least 2 recurring tasks
        self.assertGreaterEqual(len(recurring_tasks), 2)
        
        # All tasks should have recurrence info
        for task in recurring_tasks:
            self.assertIn("recurrence", task)

if __name__ == "__main__":
    unittest.main()