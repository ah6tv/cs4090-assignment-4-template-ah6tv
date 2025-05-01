from behave import given, when, then
import sys
import os
import datetime
import uuid
from unittest.mock import patch, MagicMock

# Add parent directory to path to import tasks module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from tasks import (
    load_tasks, save_tasks, filter_tasks_by_priority,
    filter_tasks_by_completion, filter_tasks_by_category,
    search_tasks, get_overdue_tasks, generate_unique_id,
    add_tags_to_task, remove_tag_from_task, filter_tasks_by_tag,
    sort_tasks, add_task, add_recurring_task, complete_task,
    generate_next_occurrence, list_recurring_tasks
)
# Mock version for testing
def generate_unique_id(tasks=None):
    """Generate a unique ID for testing purposes"""
    return str(uuid.uuid4())
# Common steps ------------------------------------------------------------

@given('the to-do list is empty')
def step_empty_todo_list(context):
    context.tasks = []
    context.mock_save = patch('tasks.save_tasks').start()
    context.mock_load = patch('tasks.load_tasks', return_value=context.tasks).start()

# Task creation steps -----------------------------------------------------

@given('I have a basic task with title "{title}"')
def step_have_task(context, title):
    _create_task(context, title)

@given('I have a task with title "{title}" that is completed')
def step_have_completed_task(context, title):
    task = _create_task(context, title)
    task["completed"] = True

@given('I have a task with title "{title}" and tags "{tags}"')
def step_have_task_with_tags(context, title, tags):
    task = _create_task(context, title)
    task["tags"] = [tag.strip() for tag in tags.split(',')]

@given('I have a recurring task with title "{title}" and pattern "{pattern}"')
def step_have_recurring_task(context, title, pattern):
    task = _create_task(context, title)
    task["recurrence"] = {
        "pattern": pattern,
        "interval": 1
    }

@given('I have the following tasks')
def step_have_tasks_table(context):
    if not hasattr(context, 'tasks'):
        context.tasks = []
    
    for row in context.table:
        task = {
            "id": generate_unique_id(),
            "title": row['title'],
            "description": row.get('description', ''),
            "priority": row.get('priority', 'Medium'),
            "category": row.get('category', 'Work'),
            "due_date": row.get('due_date', datetime.datetime.now().strftime("%Y-%m-%d")),
            "completed": row.get('completed', 'false').lower() == 'true',
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Handle recurrence if specified
        if 'recurrence_pattern' in row.headings and row['recurrence_pattern']:
            task["recurrence"] = {
                "pattern": row['recurrence_pattern'],
                "interval": int(row.get('recurrence_interval', 1))
            }
        
        # Handle tags if specified
        if 'tags' in row.headings and row['tags']:
            task["tags"] = [tag.strip() for tag in row['tags'].split(',')]
            
        context.tasks.append(task)

@given('I have the following tasks with tags')
def step_have_tasks_with_tags(context):
    step_have_tasks_table(context)  # Reuse the table implementation

# Task actions ------------------------------------------------------------

@when('I add a task with title "{title}"')
def step_add_task_with_title(context, title):
    new_task = {
        "title": title,
        "description": "",
        "priority": "Medium",
        "category": "Work",
        "due_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "completed": False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    add_task(context.tasks, new_task)

@when('I add a task with the following details')
def step_add_task_with_details(context):
    row = context.table[0]
    new_task = {
        "title": row['title'],
        "description": row.get('description', ''),
        "priority": row.get('priority', 'Medium'),
        "category": row.get('category', 'Work'),
        "due_date": row.get('due_date', datetime.datetime.now().strftime("%Y-%m-%d")),
        "completed": False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    add_task(context.tasks, new_task)

@when('I add a recurring task with the following details')
def step_add_recurring_task(context):
    row = context.table[0]
    new_task = {
        "title": row['title'],
        "description": row.get('description', ''),
        "priority": row.get('priority', 'Medium'),
        "category": row.get('category', 'Work'),
        "due_date": row.get('due_date', datetime.datetime.now().strftime("%Y-%m-%d")),
        "completed": False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recurrence": {
            "pattern": row['pattern'],
            "interval": int(row['interval'])
        }
    }
    add_recurring_task(context.tasks, new_task)

@when('I mark the task "{title}" as complete')
def step_mark_task_complete(context, title):
    task = _find_task_by_title(context, title)
    complete_task(context.tasks, task["id"])

@when('I mark the task "{title}" as incomplete')
def step_mark_task_incomplete(context, title):
    task = _find_task_by_title(context, title)
    if task["completed"]:
        complete_task(context.tasks, task["id"])

@when('I add the tags "{tags}" to the task')
def step_add_tags_to_task(context, tags):
    task = context.tasks[0]  # Assuming we're working with the first task
    tag_list = [tag.strip() for tag in tags.split(',')]
    add_tags_to_task(context.tasks, task["id"], tag_list)

@when('I remove the tag "{tag}" from the task')
def step_remove_tag_from_task(context, tag):
    task = context.tasks[0]  # Assuming we're working with the first task
    remove_tag_from_task(context.tasks, task["id"], tag)

# Filtering actions -------------------------------------------------------

@when('I filter tasks by completion status "{status}"')
def step_filter_by_completion(context, status):
    completion_status = status.lower() == 'true'
    context.filtered_tasks = filter_tasks_by_completion(context.tasks, completion_status)

@when('I filter tasks by priority "{priority}"')
def step_filter_by_priority(context, priority):
    context.filtered_tasks = filter_tasks_by_priority(context.tasks, priority)

@when('I filter tasks by category "{category}"')
def step_filter_by_category(context, category):
    context.filtered_tasks = filter_tasks_by_category(context.tasks, category)

@when('I search for tasks containing "{keyword}"')
def step_search_tasks(context, keyword):
    context.filtered_tasks = search_tasks(context.tasks, keyword)

@when('I filter tasks by tag "{tag}"')
def step_filter_by_tag(context, tag):
    context.filtered_tasks = filter_tasks_by_tag(context.tasks, tag)

@when('I list all recurring tasks')
def step_list_recurring_tasks(context):
    context.filtered_tasks = list_recurring_tasks(context.tasks)

# Verification steps ------------------------------------------------------

@then('the to-do list should contain {count:d} task(s)')
def step_todo_list_count(context, count):
    assert len(context.tasks) == count, f"Expected {count} tasks, got {len(context.tasks)}"

@then('the task should have the title "{title}"')
def step_task_has_title(context, title):
    assert any(task['title'] == title for task in context.tasks), f"No task with title '{title}'"

@then('the task should have the priority "{priority}"')
def step_task_has_priority(context, priority):
    assert any(task.get('priority') == priority for task in context.tasks), f"No task with priority '{priority}'"

@then('the task should have the category "{category}"')
def step_task_has_category(context, category):
    assert any(task.get('category') == category for task in context.tasks), f"No task with category '{category}'"

@then('the task "{title}" should be marked as complete')
def step_task_is_complete(context, title):
    task = _find_task_by_title(context, title)
    assert task['completed'], f"Task '{title}' is not complete"

@then('the task "{title}" should be marked as incomplete')
def step_task_is_incomplete(context, title):
    task = _find_task_by_title(context, title)
    assert not task['completed'], f"Task '{title}' is not incomplete"

@then('the task should have the tags "{tags}"')
def step_task_has_tags(context, tags):
    expected_tags = [tag.strip() for tag in tags.split(',')]
    task = context.tasks[0]  # Assuming we're checking the first task
    actual_tags = task.get('tags', [])
    assert set(actual_tags) == set(expected_tags), f"Expected tags {expected_tags}, got {actual_tags}"

@then('the task should not have the tag "{tag}"')
def step_task_not_has_tag(context, tag):
    task = context.tasks[0]  # Assuming we're checking the first task
    if 'tags' in task:
        assert tag not in task['tags'], f"Task unexpectedly has tag '{tag}'"

@then('the task should be a recurring task')
def step_task_is_recurring(context):
    task = context.tasks[0]  # Assuming we're checking the first task
    assert 'recurrence' in task, "Task is not a recurring task"

@then('the task should have a recurrence pattern of "{pattern}"')
def step_task_has_recurrence_pattern(context, pattern):
    task = context.tasks[0]  # Assuming we're checking the first task
    assert task['recurrence']['pattern'] == pattern, \
        f"Expected pattern '{pattern}', got '{task['recurrence']['pattern']}'"

@then('the task should have a recurrence interval of {interval:d}')
def step_task_has_recurrence_interval(context, interval):
    task = context.tasks[0]  # Assuming we're checking the first task
    assert task['recurrence']['interval'] == interval, \
        f"Expected interval {interval}, got {task['recurrence']['interval']}"

@then('a new task "{title}" should be generated')
def step_new_task_generated(context, title):
    matching_tasks = [t for t in context.tasks if t['title'] == title]
    assert len(matching_tasks) >= 2, f"Expected at least 2 tasks with title '{title}'"

@then('the new task should have a due date {days:d} days after the original')
def step_new_task_due_date(context, days):
    # Find tasks with same title (assuming most recent is the new one)
    title = context.tasks[-1]['title']
    matching_tasks = [t for t in context.tasks if t['title'] == title]
    matching_tasks.sort(key=lambda t: t['created_at'])
    
    original_date = datetime.datetime.strptime(matching_tasks[0]['due_date'], "%Y-%m-%d")
    new_date = datetime.datetime.strptime(matching_tasks[-1]['due_date'], "%Y-%m-%d")
    delta = (new_date - original_date).days
    
    assert delta == days, f"Expected {days} days difference, got {delta}"

@then('I should see {count:d} tasks in the filtered list')
def step_filtered_list_count(context, count):
    assert len(context.filtered_tasks) == count, \
        f"Expected {count} tasks, got {len(context.filtered_tasks)}"

@then('the filtered list should include "{title}"')
def step_filtered_list_includes(context, title):
    assert any(t['title'] == title for t in context.filtered_tasks), \
        f"Task '{title}' not found in filtered list"

@then('the filtered list should not include "{title}"')
def step_filtered_list_excludes(context, title):
    assert not any(t['title'] == title for t in context.filtered_tasks), \
        f"Task '{title}' unexpectedly found in filtered list"

@then('I should see {count:d} tasks in the list')
def step_list_contains_count(context, count):
    assert len(context.filtered_tasks) == count, \
        f"Expected {count} tasks, got {len(context.filtered_tasks)}"

@then('the list should include "{title}"')
def step_list_includes(context, title):
    assert any(t['title'] == title for t in context.filtered_tasks), \
        f"Task '{title}' not found in list"

@then('the list should not include "{title}"')
def step_list_excludes(context, title):
    assert not any(t['title'] == title for t in context.filtered_tasks), \
        f"Task '{title}' unexpectedly found in list"

# Helper functions --------------------------------------------------------

def _create_task(context, title, **kwargs):
    """Helper to create a task with default values"""
    if not hasattr(context, 'tasks'):
        context.tasks = []
    
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": "",
        "priority": "Medium",
        "category": "Work",
        "due_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "completed": False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    task.update(kwargs)
    context.tasks.append(task)
    return task

def _find_task_by_title(context, title):
    """Helper to find a task by title"""
    for task in context.tasks:
        if task['title'] == title:
            return task
    raise AssertionError(f"No task found with title '{title}'")