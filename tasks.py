import json
import os
from datetime import datetime, timedelta
from copy import deepcopy
from dateutil.relativedelta import relativedelta
import uuid

# File path for task storage
DEFAULT_TASKS_FILE = "tasks.json"

def load_tasks(file_path=DEFAULT_TASKS_FILE):
    """
    Load tasks from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing tasks
    Returns:
        list: List of task dictionaries, empty list if file doesn't exist
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # Handle corrupted JSON file
        print(f"Warning: {file_path} contains invalid JSON. Creating new tasks list.")
        return []

def save_tasks(tasks, file_path=DEFAULT_TASKS_FILE):
    """
    Save tasks to a JSON file.
    Args:
        tasks (list): List of task dictionaries
        file_path (str): Path to save the JSON file
    """
    with open(file_path, "w") as f:
        json.dump(tasks, f, indent=2)

def generate_unique_id(tasks):
    """
    Generate a unique ID for a new task.
    Args:
        tasks (list): List of existing task dictionaries
    Returns:
        int: A unique ID for a new task
    """
    if not tasks:
        return 1
    
    # Convert all IDs to integers for comparison
    ids = []
    for task in tasks:
        task_id = task.get("id")
        if isinstance(task_id, str):
            # Try to convert string IDs that are numeric
            try:
                ids.append(int(task_id))
            except ValueError:
                # If it's a UUID or other non-numeric string, skip it
                continue
        else:
            ids.append(task_id)
    
    # If no valid numeric IDs were found, return 1
    if not ids:
        return 1
        
    return max(ids, default=0) + 1

def filter_tasks_by_priority(tasks, priority):
    """
    Filter tasks by priority level.
    Args:
        tasks (list): List of task dictionaries
        priority (str): Priority level to filter by (High, Medium, Low)
    Returns:
        list: Filtered list of tasks matching the priority
    """
    return [task for task in tasks if task.get("priority") == priority]

def filter_tasks_by_category(tasks, category):
    """
    Filter tasks by category.
    Args:
        tasks (list): List of task dictionaries
        category (str): Category to filter by
    Returns:
        list: Filtered list of tasks matching the category
    """
    return [task for task in tasks if task.get("category") == category]

def filter_tasks_by_completion(tasks, completed=True):
    """
    Filter tasks by completion status.
    Args:
        tasks (list): List of task dictionaries
        completed (bool): Completion status to filter by
    Returns:
        list: Filtered list of tasks matching the completion status
    """
    return [task for task in tasks if task.get("completed") == completed]

def search_tasks(tasks, query):
    """
    Search tasks by a text query in title and description.
    Args:
        tasks (list): List of task dictionaries
        query (str): Search query
    Returns:
        list: Filtered list of tasks matching the search query
    """
    query = query.lower()
    return [
        task for task in tasks
        if query in task.get('title', '').lower() or query in task.get('description', '').lower()
    ]

def get_overdue_tasks(tasks):
    """
    Get tasks that are past their due date and not completed.
    Args:
        tasks (list): List of task dictionaries
    Returns:
        list: List of overdue tasks
    """
    today = datetime.now().strftime("%Y-%m-%d")
    overdue = []
    for task in tasks:
        # Skip tasks with no due date
        if not task.get("due_date"):
            continue
        # Skip completed tasks
        if task.get("completed", False):
            continue
        try:
            # Only add tasks with a valid due date that is in the past
            if task["due_date"] < today:
                overdue.append(task)
        except (ValueError, TypeError):
            # Skip tasks with invalid date format
            continue
    return overdue

# Feature 1: Task Tagging System

def add_tags_to_task(tasks, task_id, tags, file_path=DEFAULT_TASKS_FILE):
    """
    Add tags to a specific task.
    
    Args:
        tasks (list): List of task dictionaries
        task_id (int): ID of the task to update
        tags (list): List of tags to add
        file_path (str): Path to save the JSON file
        
    Returns:
        bool: True if tags were added successfully, False otherwise
    """
    for task in tasks:
        if task["id"] == task_id:
            # Create tags list if it doesn't exist
            if "tags" not in task:
                task["tags"] = []
            
            # Add unique tags that aren't already in the list
            task["tags"].extend([tag for tag in tags if tag not in task["tags"]])
            
            # Save the updated tasks
            save_tasks(tasks, file_path)
            return True
    
    return False

def remove_tag_from_task(tasks, task_id, tag, file_path=DEFAULT_TASKS_FILE):
    """
    Remove a tag from a specific task.
    
    Args:
        tasks (list): List of task dictionaries
        task_id (int): ID of the task to update
        tag (str): Tag to remove
        file_path (str): Path to save the JSON file
        
    Returns:
        bool: True if tag was removed successfully, False otherwise
    """
    for task in tasks:
        if task["id"] == task_id:
            # Check if task has tags
            if "tags" in task and tag in task["tags"]:
                task["tags"].remove(tag)
                save_tasks(tasks, file_path)
                return True
    
    return False

def filter_tasks_by_tag(tasks, tag):
    """
    Filter tasks by a specific tag.
    
    Args:
        tasks (list): List of task dictionaries
        tag (str): Tag to filter by
        
    Returns:
        list: Filtered list of tasks containing the tag
    """
    return [
        task for task in tasks 
        if "tags" in task and tag in task["tags"]
    ]

# Feature 2: Task Sorting

def sort_tasks(tasks, sort_by, ascending=True):
    """
    Sort tasks by a specific attribute.
    
    Args:
        tasks (list): List of task dictionaries
        sort_by (str): Attribute to sort by (e.g., 'due_date', 'priority', 'title')
        ascending (bool): Sort in ascending order if True, descending if False
        
    Returns:
        list: Sorted list of tasks
    """
    # Handle special case for priority sorting
    if sort_by == "priority":
        # Define priority order: High > Medium > Low
        priority_order = {"High": 3, "Medium": 2, "Low": 1, None: 0}
        
        # Create a copy of tasks to avoid modifying the original
        sorted_tasks = tasks.copy()
        
        # Sort using priority_order dictionary for comparison
        sorted_tasks.sort(
            key=lambda task: priority_order.get(task.get(sort_by), 0),
            reverse=not ascending  # Reverse if not ascending
        )
        return sorted_tasks
    
    # For other attributes, use regular sorting
    return sorted(
        tasks,
        key=lambda task: (task.get(sort_by) is None, task.get(sort_by, "")),
        reverse=not ascending
    )

# Feature 3: Recurring Tasks

def add_task(tasks, task_data, file_path=DEFAULT_TASKS_FILE):
    """
    Add a new task to the task list.
    
    Args:
        tasks (list): List of task dictionaries
        task_data (dict): Data for the new task
        file_path (str): Path to save the JSON file
        
    Returns:
        int: ID of the newly created task
    """
    # Generate a unique ID for the new task
    task_id = generate_unique_id(tasks)
    
    # Create the new task dictionary
    new_task = {
        "id": task_id,
        "completed": False,  # Default to not completed
        **task_data
    }
    
    # Add the task to the list
    tasks.append(new_task)
    
    # Save the updated tasks
    save_tasks(tasks, file_path)
    
    return task_id

def add_recurring_task(tasks, task_data, file_path=DEFAULT_TASKS_FILE):
    """
    Add a new recurring task to the task list.
    
    Args:
        tasks (list): List of task dictionaries
        task_data (dict): Data for the new recurring task
        file_path (str): Path to save the JSON file
        
    Returns:
        int: ID of the newly created recurring task
    """
    # Ensure recurrence information is present
    if "recurrence" not in task_data:
        raise ValueError("Recurring task must include recurrence information")
    
    # Set the first due date if not provided
    if "due_date" not in task_data:
        task_data["due_date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Add the task using the regular add_task function
    return add_task(tasks, task_data, file_path)

def complete_task(tasks, task_id, file_path=DEFAULT_TASKS_FILE):
    """
    Toggle the completion status of a task. If it's a recurring task and it's completed,
    generate the next occurrence.
    
    Args:
        tasks (list): List of task dictionaries
        task_id (int or str): ID of the task to toggle completion status
        file_path (str): Path to save the JSON file
        
    Returns:
        bool: True if task was successfully updated, False otherwise
    """
    for task in tasks:
        if task["id"] == task_id:
            # Toggle the completion status
            task["completed"] = not task["completed"]
            
            if task["completed"]:
                task["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            else:
                task.pop("completed_date", None)  # Remove completion date if uncompleted

            # Handle recurrence - Only create new instance if task is now completed
            if "recurrence" in task and task["completed"]:
                pattern = task["recurrence"].get("pattern")
                interval = int(task["recurrence"].get("interval", 1))
                due_date_str = task.get("due_date")

                if pattern and due_date_str:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    
                    if pattern == "daily":
                        new_due = due_date + timedelta(days=interval)
                    elif pattern == "weekly":
                        new_due = due_date + timedelta(weeks=interval)
                    elif pattern == "monthly":
                        new_due = due_date + relativedelta(months=interval)
                    else:
                        new_due = None

                    if new_due:
                        # Create a copy of the task for the new occurrence
                        new_task = deepcopy(task)
                        new_task["id"] = str(uuid.uuid4())  # Generate new UUID
                        new_task["completed"] = False  # Reset completion status
                        new_task.pop("completed_date", None)  # Remove completion date
                        new_task["due_date"] = new_due.strftime("%Y-%m-%d")  # Set new due date
                        tasks.append(new_task)  # Add new task to task list

            save_tasks(tasks, file_path)
            return True

    return False


def generate_next_occurrence(tasks, task_id, file_path=DEFAULT_TASKS_FILE):
    """
    Generate the next occurrence of a recurring task after it's completed.
    
    Args:
        tasks (list): List of task dictionaries
        task_id (int): ID of the completed recurring task
        file_path (str): Path to save the JSON file
        
    Returns:
        int: ID of the newly created next occurrence task, or None if not a recurring task
    """
    # Find the task by ID
    task = next((t for t in tasks if t["id"] == task_id), None)
    
    if not task or "recurrence" not in task:
        return None
    
    # Create a copy of the task for the next occurrence
    next_task = task.copy()
    
    # Generate a new ID
    next_task["id"] = generate_unique_id(tasks)
    
    # Reset completion status
    next_task["completed"] = False
    if "completed_date" in next_task:
        del next_task["completed_date"]
    
    # Calculate the next due date based on recurrence pattern
    if "due_date" in task:
        current_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
        
        if task["recurrence"]["pattern"] == "daily":
            days = task["recurrence"]["interval"]
            next_date = current_date + timedelta(days=days)
        elif task["recurrence"]["pattern"] == "weekly":
            days = 7 * task["recurrence"]["interval"]
            next_date = current_date + timedelta(days=days)
        elif task["recurrence"]["pattern"] == "monthly":
            # Add months (approximate)
            months = task["recurrence"]["interval"]
            # Simple implementation for monthly recurrence
            next_month = current_date.month + months
            next_year = current_date.year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            
            # Try to use the same day, but adjust for months with fewer days
            try:
                next_date = current_date.replace(year=next_year, month=next_month)
            except ValueError:
                # Handle edge case like Feb 29 -> Feb 28
                last_day = [31, 29 if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0) else 28, 
                            31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                next_date = current_date.replace(year=next_year, month=next_month, 
                                              day=min(current_date.day, last_day[next_month-1]))
        
        next_task["due_date"] = next_date.strftime("%Y-%m-%d")
    
    # Decrement end_after if it exists
    if "end_after" in task["recurrence"]:
        next_task["recurrence"]["end_after"] = task["recurrence"]["end_after"] - 1
        
        # If this was the last occurrence, don't create a new one
        if next_task["recurrence"]["end_after"] <= 0:
            return None
    
    # Add the new task to the list
    tasks.append(next_task)
    save_tasks(tasks, file_path)
    
    return next_task["id"]

def list_recurring_tasks(tasks):
    """
    List all recurring tasks.
    
    Args:
        tasks (list): List of task dictionaries
        
    Returns:
        list: List of recurring tasks
    """
    return [task for task in tasks if "recurrence" in task]