import pytest
from tasks import (
    filter_tasks_by_priority,
    filter_tasks_by_category,
    generate_unique_id,
    get_overdue_tasks,
    save_tasks,
    load_tasks
)
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch, Mock
import json
from importlib import import_module
import sys
import os
from app import run_html_report

# Import the app module to access its functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
app = import_module('app')

# Set testing environment variable
os.environ['TESTING'] = '1'

# Parameterized Test Examples
@pytest.mark.parametrize("tasks, priority, expected_count", [
    # Test different priority combinations
    ([{"priority": "High"}], "High", 1),
    ([{"priority": "High"}, {"priority": "Medium"}], "High", 1),
    ([{"priority": "High"}, {"priority": "High"}], "High", 2),
    ([{"priority": "Low"}, {"priority": "Low"}], "Low", 2),
    # Edge cases
    ([], "High", 0),
    ([{"priority": "High"}], "Medium", 0),
    ([{"priority": "High"}], "Critical", 0),
])
def test_filter_tasks_by_priority_parameterized(tasks, priority, expected_count):
    """Test priority filtering with multiple input combinations"""
    filtered = filter_tasks_by_priority(tasks, priority)
    assert len(filtered) == expected_count

@pytest.mark.parametrize("tasks, category, expected_count", [
    # Test different category combinations
    ([{"category": "Work"}], "Work", 1),
    ([{"category": "Work"}, {"category": "Personal"}], "Work", 1),
    ([{"category": "Work"}, {"category": "Work"}], "Work", 2),
    # Edge cases
    ([], "Work", 0),
    ([{"category": "Work"}], "School", 0),
])
def test_filter_tasks_by_category_parameterized(tasks, category, expected_count):
    """Test category filtering with multiple input combinations"""
    filtered = filter_tasks_by_category(tasks, category)
    assert len(filtered) == expected_count

@pytest.mark.parametrize("existing_ids, expected_id", [
    # Test ID generation scenarios
    ([], 1),
    ([1], 2),
    ([1, 2, 3], 4),
    ([5, 10, 3], 11),
    # Edge case with non-sequential IDs
    ([100, 50, 75], 101),
])
def test_generate_unique_id_parameterized(existing_ids, expected_id):
    """Test ID generation with various existing ID lists"""
    tasks = [{"id": id} for id in existing_ids]
    assert generate_unique_id(tasks) == expected_id

# Parameterized tests for date handling
@pytest.mark.parametrize("due_date_offset, completed, expected_overdue", [
    # Yesterday - should be overdue if not completed
    (-1, False, True),
    # Yesterday but completed - not overdue
    (-1, True, False),
    # Today - not overdue
    (0, False, False),
    # Tomorrow - not overdue
    (1, False, False),
])
def test_overdue_calculation_parameterized(due_date_offset, completed, expected_overdue):
    """Test overdue calculation with different date scenarios"""
    test_date = (datetime.now() + timedelta(days=due_date_offset)).strftime("%Y-%m-%d")
    task = {"due_date": test_date, "completed": completed}
    overdue = get_overdue_tasks([task])
    assert (len(overdue) == 1) == expected_overdue

def test_load_tasks_with_mock():
    """Test loading tasks with mocked file"""
    mock_data = '[{"id": 1, "title": "Mock Task"}]'
    
    with patch("builtins.open", mock_open(read_data=mock_data)):
        tasks = load_tasks("dummy_path.json")
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Mock Task"
        assert tasks[0]["id"] == 1

def test_load_tasks_empty_file_mock():
    """Test loading tasks from empty file"""
    with patch("builtins.open", mock_open(read_data="")):
        tasks = load_tasks("empty.json")
        assert tasks == []

def test_load_tasks_invalid_json_mock():
    """Test loading tasks from invalid JSON"""
    with patch("builtins.open", mock_open(read_data="Not JSON")):
        tasks = load_tasks("invalid.json")
        assert tasks == []

def test_save_tasks_with_mock():
    """Test saving tasks with mocked file"""
    test_tasks = [{"id": 1, "title": "Test Task"}]
    mock_file = mock_open()
    
    with patch("builtins.open", mock_file):
        with patch("json.dump") as mock_json_dump:
            save_tasks(test_tasks, "dummy_path.json")
    
    # Verify file operations
    mock_file.assert_called_once_with("dummy_path.json", "w")
    
    # Verify json.dump was called with the right arguments including indent=2
    mock_json_dump.assert_called_once_with(test_tasks, mock_file(), indent=2)

# Mocking DateTime for Overdue Tests
def test_get_overdue_tasks_with_mock_date():
    """Test overdue tasks with mocked datetime"""
    test_tasks = [
        {"id": 1, "due_date": "2023-01-01", "completed": False},
        {"id": 2, "due_date": "2023-01-01", "completed": True}
    ]
    
    # Mock datetime.now() to return a fixed date
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 2)
        overdue = get_overdue_tasks(test_tasks)
        
        assert len(overdue) == 1
        assert overdue[0]["id"] == 1

# Mocking System Functions
def test_file_not_found_handling_mock():
    """Test handling of missing file"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        tasks = load_tasks("nonexistent.json")
        assert tasks == []

# Comprehensive Mocking Test
def test_complete_file_operation_flow_mock():
    """Test complete save/load cycle with mocks"""
    test_tasks = [{"id": 1, "title": "Mock Flow Task"}]
    mock_file = mock_open()
    
    with patch("builtins.open", mock_file):
        # First save the tasks
        save_tasks(test_tasks, "flow_test.json")
        
        # Then mock reading them back
        mock_file().read.return_value = json.dumps(test_tasks)
        
        # Now load them
        loaded_tasks = load_tasks("flow_test.json")
        assert loaded_tasks == test_tasks

@pytest.fixture
def html_setup_test_files(tmp_path):
    """Fixture to set up test files for report generation tests"""
    test_file = tmp_path / "test_tasks.json"
    test_file.write_text(json.dumps([{"id": 1, "title": "Test Task"}]))
    return test_file

def test_html_report_generation(tmp_path):
    """Test that HTML report generation works"""
    with patch("subprocess.run") as mock_run:
        # Mock a successful subprocess run
        mock_result = Mock()
        mock_result.stdout = "HTML report generated"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Call the function
        output, report_path = run_html_report()

        # Verify the call
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        
        # Verify pytest command structure
        assert args[0][0] == "python"
        assert args[0][1] == "-m"
        assert args[0][2] == "pytest"
        
        # Verify HTML report argument exists
        html_args = [arg for arg in args[0] if arg.startswith('--html')]
        assert len(html_args) == 1
        assert html_args[0] == "--html=test_report.html"
        
        # Verify coverage arguments
        assert "--cov=tasks" in args[0]
        assert "--cov-report=html:cov_html" in args[0]
        
        # Verify return values
        assert output == "HTML report generated"
        assert report_path == "test_report.html"
def test_html_report_failure():
    """Test HTML report generation failure case"""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Test error")
        
        result = app.run_html_report()
        assert "Error generating HTML report" in result[0]
        assert result[1] is None