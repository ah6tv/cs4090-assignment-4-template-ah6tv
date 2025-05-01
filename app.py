import streamlit as st
import pandas as pd
import subprocess
import json
import sys
import os
from datetime import datetime, timedelta
from tasks import (
    load_tasks, 
    save_tasks, 
    filter_tasks_by_priority,
    filter_tasks_by_completion, 
    filter_tasks_by_category, 
    search_tasks,
    get_overdue_tasks,
    generate_unique_id,
    add_tags_to_task,
    remove_tag_from_task,
    filter_tasks_by_tag,
    sort_tasks,
    add_task,
    add_recurring_task,
    complete_task,
    generate_next_occurrence,
    list_recurring_tasks
)
import tempfile
import webbrowser
from unittest.mock import patch

def run_tests(test_file=None, extra_args=None):
    """
    Run pytest tests and return the results
    
    Args:
        test_file (str, optional): Specific test file to run
        extra_args (list, optional): Additional pytest arguments
        
    Returns:
        str: Test results as string
    """
    # Configure Python path to include the current directory
    env = os.environ.copy()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = current_dir
    
    cmd = ["python", "-m", "pytest", "-v"]
    
    if test_file:
        cmd.append(test_file)
    
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running tests: {str(e)}"

def run_coverage():
    """Run pytest with coverage reporting"""
    try:
        # Configure Python path to include the current directory
        env = os.environ.copy()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = current_dir
            
        cmd = ["python", "-m", "pytest", "--cov=tasks", "--cov-report", "term"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running coverage: {str(e)}"

def run_basic_tests_with_coverage():
    """Run basic tests with coverage reporting"""
    cmd = [
        "pytest",
        "tests/test_basic.py",  
        "-v",                   
        "--cov=tasks",          
        "--cov-report=term"     
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running tests: {str(e)}"
        
def run_pytest(test_path=None, extra_args=None):
    """Run pytest with specified arguments"""
    cmd = ["pytest", "-v"]
    
    if test_path:
        cmd.append(test_path)
    
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running tests: {str(e)}"

def run_html_report():
    """Run pytest with HTML report generation"""
    try:
        # Configure Python path to include the current directory
        env = os.environ.copy()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = current_dir
            
        report_file = "test_report.html"
        cmd = [
            "python", "-m", "pytest", 
            "--cov=tasks",
            "--cov-report=html:cov_html",
            "--html=" + report_file,
            "--self-contained-html",
            "-k html"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        # Return both the console output and the report path
        return result.stdout + result.stderr, report_file
    except Exception as e:
        return f"Error generating HTML report: {str(e)}", None

def run_tdd_tests():
    """Run TDD feature tests"""
    try:
        # Configure Python path to include the current directory
        env = os.environ.copy()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = current_dir
            
        # Update the path to point to the tests directory
        cmd = ["python", "-m", "pytest", "tests/test_tdd.py", "-v"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running TDD tests: {str(e)}"

def run_bdd_tests():
    """Run BDD feature tests using behave"""
    try:
        # Configure Python path to include the current directory
        env = os.environ.copy()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = current_dir
            
        # Run behave on the features directory
        cmd = ["behave", "features/", "-v"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running BDD tests: {str(e)}"

def main():
    st.title("To-Do Application")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tasks", "Unit Tests", "Pytest Features", "TDD Features", "BDD Tests"])

    with tab1:
        # Load existing tasks
        all_tasks = load_tasks()
        
        # Sidebar for adding new tasks
        st.sidebar.header("Add New Task")
        
        # Add option to choose between regular and recurring task
        task_type = st.sidebar.radio("Task Type", ["Regular Task", "Recurring Task"])
        
        # Task creation form
        with st.sidebar.form("new_task_form"):
            task_title = st.text_input("Task Title")
            task_description = st.text_area("Description")
            task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
            task_due_date = st.date_input("Due Date")
            
            # Add tags input
            task_tags = st.text_input("Tags (comma separated)")
            
            # Additional fields for recurring tasks
            if task_type == "Recurring Task":
                recurrence_pattern = st.selectbox("Recurrence Pattern", ["daily", "weekly", "monthly"])
                recurrence_interval = st.number_input("Interval", min_value=1, value=1)
                recurrence_end_after = st.number_input("End After (occurrences)", min_value=0, value=0, 
                                                      help="0 means no end date")
            
            submit_button = st.form_submit_button("Add Task")
        
        if submit_button and task_title:
            # Process tags if provided
            tags_list = [tag.strip() for tag in task_tags.split(',')] if task_tags else []
            
            # Create basic task dictionary
            new_task = {
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add tags if provided
            if tags_list:
                new_task["tags"] = tags_list
            
            # Handle recurring task
            if task_type == "Recurring Task":
                new_task["recurrence"] = {
                    "pattern": recurrence_pattern,
                    "interval": recurrence_interval
                }
                
                # Add end_after if specified
                if recurrence_end_after > 0:
                    new_task["recurrence"]["end_after"] = recurrence_end_after
                
                # Add task using the recurring function
                add_recurring_task(all_tasks, new_task)
            else:
                # Add regular task
                add_task(all_tasks, new_task)
            
            st.sidebar.success("Task added successfully!")
        
        # Main area to display tasks
        st.header("Your Tasks")
        
        # Enhanced filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category = st.selectbox("Filter by Category", ["All"] + list(set([task.get("category", "") for task in all_tasks if task.get("category")]) if all_tasks else []))
        with col2:
            filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
        with col3:
            # Get unique tags from all tasks
            all_tags = set()
            for task in all_tasks:
                if "tags" in task:
                    all_tags.update(task["tags"])
            filter_tag = st.selectbox("Filter by Tag", ["All"] + sorted(list(all_tags)))
        
        show_completed = st.checkbox("Show Completed Tasks")
        
        # Sorting options
        sort_by = st.selectbox("Sort By", ["Due Date", "Priority", "Title", "Category"])
        sort_order = st.radio("Sort Order", ["Ascending", "Descending"], horizontal=True)
        
        # Apply filters
        filtered_tasks = all_tasks.copy()
        if filter_category != "All":
            filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
        if filter_priority != "All":
            filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
        if filter_tag != "All":
            filtered_tasks = filter_tasks_by_tag(filtered_tasks, filter_tag)
        if not show_completed:
            filtered_tasks = [task for task in filtered_tasks if not task.get("completed", False)]
        
        # Apply sorting
        sort_key = sort_by.lower().replace(" ", "_")
        filtered_tasks = sort_tasks(filtered_tasks, sort_key, ascending=(sort_order == "Ascending"))
        
        # Display tasks
        if not filtered_tasks:
            st.info("No tasks match your filters.")
        
        for task in filtered_tasks:
            col1, col2 = st.columns([4, 1])
            with col1:
                if task.get("completed", False):
                    st.markdown(f"~~**{task['title']}**~~")
                else:
                    st.markdown(f"**{task['title']}**")
                st.write(task.get("description", ""))
                
                # Show metadata
                meta_info = [
                    f"Due: {task.get('due_date', 'N/A')}",
                    f"Priority: {task.get('priority', 'N/A')}",
                    f"Category: {task.get('category', 'N/A')}"
                ]
                
                # Add recurrence info if it's a recurring task
                if "recurrence" in task:
                    pattern = task["recurrence"]["pattern"]
                    interval = task["recurrence"]["interval"]
                    recurrence_text = f"Recurring: Every {interval} {pattern}"
                    meta_info.append(recurrence_text)
                
                # Add tags if available
                if "tags" in task and task["tags"]:
                    tags_text = f"Tags: {', '.join(task['tags'])}"
                    meta_info.append(tags_text)
                
                st.caption(" | ".join(meta_info))

            with col2:
                task_actions = st.container()
                
                # Complete/Undo button
                if task_actions.button("Complete" if not task.get("completed", False) else "Undo", key=f"complete_{task['id']}"):
                    is_recurring = "recurrence" in task
                    
                    # Mark the task as complete
                    complete_task(all_tasks, task["id"])
                    
                    # If it's a recurring task, generate the next occurrence
                    if is_recurring and not task.get("completed", False):
                        generate_next_occurrence(all_tasks, task["id"])
                    
                    st.rerun()
                
                # Delete button
                if task_actions.button("Delete", key=f"delete_{task['id']}"):
                    all_tasks = [t for t in all_tasks if t["id"] != task["id"]]
                    save_tasks(all_tasks)
                    st.rerun()
                
                # Manage tags (expandable)
                with task_actions.expander("Manage Tags"):
                    # Show current tags
                    if "tags" in task and task["tags"]:
                        st.write("Current tags:")
                        for tag in task["tags"]:
                            col1, col2 = st.columns([3, 1])
                            col1.write(tag)
                            if col2.button("Remove", key=f"remove_tag_{task['id']}_{tag}"):
                                remove_tag_from_task(all_tasks, task["id"], tag)
                                st.rerun()
                    
                    # Add new tag
                    new_tag = st.text_input("Add tag", key=f"add_tag_{task['id']}")
                    if st.button("Add", key=f"add_tag_btn_{task['id']}"):
                        if new_tag:
                            add_tags_to_task(all_tasks, task["id"], [new_tag])
                            st.rerun()
    
    with tab2:
        st.header("Test Suite")
        st.markdown("""
        This tab allows you to run automated unit tests for the To-Do List application.
        The tests verify that all core functionality is working correctly.
        """)
        
        st.subheader("Unit Tests")
        st.markdown("""
        Run basic unit tests to verify the functionality of individual functions in the `tasks.py` module.
        These tests validate that each function works correctly in isolation.
        """)
        
        if st.button("Run Unit Tests"):
            with st.spinner("Running unit tests..."):
                test_results = run_tests("tests/test_basic.py")
                st.code(test_results, language="text")
        
        st.divider()
        
        st.subheader("Coverage Report")
        st.markdown("""
        Run tests with coverage reporting to ensure at least 90% of the code is tested.
        This helps identify any untested code paths.
        """)
        
        if st.button("Run Coverage Report"):
            with st.spinner("Generating coverage report..."):
                coverage_results = run_coverage()
                st.code(coverage_results, language="text")
        
        st.divider()
        
        st.subheader("View Unit Testing Documentation")
        st.markdown("""
        This documentation explains the approach taken for unit testing the To-Do List application.
        """)
        
        if st.button("Show Documentation"):
            try:
                with open("docs/unit_testing_approach.md", "r") as f:
                    docs_content = f.read()
                st.markdown(docs_content)
            except FileNotFoundError:
                st.error("Documentation file not found. Please make sure docs/unit_testing_approach.md exists.")
    
    with tab3:
        st.header("Pytests")
        st.markdown("This tab allows you to run automated pytest feature tests for the To-Do-List application.")

        st.subheader("Pytest Coverage")
        if st.button("Run pytest-cov"):
            with st.spinner("Running pytest-cov..."):
                result = run_basic_tests_with_coverage()
                st.code(result, language='text')
        st.divider()

        st.subheader("Parameterization")
        if st.button("Run parameterization tests"):
            with st.spinner("Running parameterization..."):
                result = run_pytest("tests/test_advanced.py", ["-k", "parameterized and not mock"])
                st.code(result, language="text")
        st.divider()

        st.subheader("Mocking")
        if st.button("Run mocking tests"):
            with st.spinner("Running mocking tests..."):
                result = run_pytest("tests/test_advanced.py", ["-k", "mock and not parameterized"])
                st.code(result, language="text")
        st.divider()

        st.subheader("report-generation in html")
        if st.button("Generate HTML report"):
            with st.spinner("Generating HTML report..."):
                report_output, report_path = run_html_report()
            st.code(report_output, language="text")
            
            if report_path and os.path.exists(report_path):
                with open(report_path, "r") as f:
                    report_html = f.read()
                st.markdown("### HTML Test Report")
                st.components.v1.html(report_html, height=800, scrolling=True)
                
                # Provide download link
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Download HTML Report",
                        data=f,
                        file_name="test_report.html",
                        mime="text/html"
                    )
            else:
                st.error("Failed to generate HTML report")
    
    with tab4:
        st.header("TDD Features")
        st.markdown("""
        This tab demonstrates the Test-Driven Development (TDD) process used to add new features to the application.
        We used TDD to implement the following features:
        
        1. **Task Tagging System**: Add and manage tags for better organization
        2. **Task Sorting**: Sort tasks by different criteria like due date, priority, etc.
        3. **Recurring Tasks**: Create tasks that repeat on a schedule
        """)
        
        st.subheader("Run TDD Tests")
        st.markdown("""
        Run the tests created during the TDD process to verify that the new features work correctly.
        """)
        
        if st.button("Run TDD Tests"):
            with st.spinner("Running TDD tests..."):
                test_results = run_tdd_tests()
                st.code(test_results, language="text")
        
        st.subheader("TDD Process Documentation")
        
        # Feature 1: Task Tagging System
        with st.expander("Feature 1: Task Tagging System"):
            st.markdown("""
            ### Task Tagging System
            
            #### Initial Test Creation
            
            We started by writing tests for the tagging functionality:
            
            1. `test_add_tags_to_task`: Tests adding tags to a task
            2. `test_remove_tag_from_task`: Tests removing a tag from a task
            3. `test_filter_tasks_by_tag`: Tests filtering tasks by tag
            
            #### Test Failure Demonstration
            
            Initially, all tests failed because the functions didn't exist:
            
            ```
            E       AttributeError: module 'tasks' has no attribute 'add_tags_to_task'
            ```
            
            #### Feature Implementation
            
            We implemented the tagging functionality:
            
            1. `add_tags_to_task`: Adds tags to a task
            2. `remove_tag_from_task`: Removes a tag from a task
            3. `filter_tasks_by_tag`: Returns tasks that have a specific tag
            
            #### Test Passing Verification
            
            After implementing the functions, all tests passed:
            
            ```
            test_add_tags_to_task PASSED
            test_remove_tag_from_task PASSED
            test_filter_tasks_by_tag PASSED
            ```
            
            #### Refactoring
            
            We integrated the tagging system into the main application UI, adding:
            - Tag filtering in the main task view
            - Tag management for each task
            - Tag input when creating new tasks
            """)
        
        # Feature 2: Task Sorting
        with st.expander("Feature 2: Task Sorting"):
            st.markdown("""
            ### Task Sorting
            
            #### Initial Test Creation
            
            We created tests for sorting tasks:
            
            1. `test_sort_tasks_by_due_date`: Tests sorting by due date
            2. `test_sort_tasks_by_priority`: Tests sorting by priority (with custom order)
            3. `test_sort_tasks_by_title`: Tests sorting alphabetically by title
            
            #### Test Failure Demonstration
            
            Initially, all tests failed because the sorting function didn't exist:
            
            ```
            E       AttributeError: module 'tasks' has no attribute 'sort_tasks'
            ```
            
            #### Feature Implementation
            
            We implemented a generic `sort_tasks` function that can sort by any attribute, with special handling for priority.
            
            #### Test Passing Verification
            
            After implementation, all sorting tests passed:
            
            ```
            test_sort_tasks_by_due_date PASSED
            test_sort_tasks_by_priority PASSED
            test_sort_tasks_by_title PASSED
            ```
            
            #### Refactoring
            
            We added sorting controls to the UI:
            - Sort by dropdown (Due Date, Priority, Title, Category)
            - Sort order selection (Ascending/Descending)
            """)
        
        # Feature 3: Recurring Tasks
        with st.expander("Feature 3: Recurring Tasks"):
            st.markdown("""
            ### Recurring Tasks
            
            #### Initial Test Creation
            
            We created tests for recurring tasks:
            
            1. `test_create_recurring_task`: Tests creating a recurring task
            2. `test_generate_next_occurrence`: Tests generating the next occurrence when a recurring task is completed
            3. `test_list_recurring_tasks`: Tests listing all recurring tasks
            
            #### Test Failure Demonstration
            
            Initially, all tests failed because the functions didn't exist:
            
            ```
            E       AttributeError: module 'tasks' has no attribute 'add_recurring_task'
            ```
            
            #### Feature Implementation
            
            We implemented the recurring task functionality:
            
            1. `add_recurring_task`: Creates a new recurring task
            2. `generate_next_occurrence`: Generates the next occurrence of a recurring task
            3. `list_recurring_tasks`: Lists all recurring tasks
            4. `complete_task`: Enhanced to handle recurring tasks
            
            #### Test Passing Verification
            
            After implementation, all recurring task tests passed:
            
            ```
            test_create_recurring_task PASSED
            test_generate_next_occurrence PASSED
            test_list_recurring_tasks PASSED
            ```
            
            #### Refactoring
            
            We integrated recurring tasks into the UI:
            - Option to create recurring tasks
            - Configuration for recurrence pattern, interval, and end date
            - Automatic generation of next task occurrence when a recurring task is completed
            - Display of recurrence information in the task list
            """)
    
    with tab5:
        st.header("BDD Tests")
        st.markdown("""
        This tab demonstrates Behavior-Driven Development (BDD) using the Behave framework.
        BDD helps define application behavior in a user-focused way through scenarios written in natural language.
        
        These scenarios follow the "Given-When-Then" pattern:
        - **Given**: the initial context
        - **When**: an event occurs
        - **Then**: the expected outcome
        """)
        
        st.subheader("Run BDD Tests")
        
        if st.button("Run BDD Tests"):
            with st.spinner("Running BDD tests..."):
                test_results = run_bdd_tests()
                st.code(test_results, language="text")
        
        st.subheader("BDD Feature Files")
        
        # Display the feature files in expandable sections
        features = [
            "add_task.feature", 
            "complete_task.feature", 
            "filter_tasks.feature", 
            "tag_tasks.feature", 
            "recurring_tasks.feature"
        ]
        
        for feature in features:
            with st.expander(f"View {feature}"):
                try:
                    with open(f"features/{feature}", "r") as f:
                        feature_content = f.read()
                    st.code(feature_content, language="gherkin")
                except FileNotFoundError:
                    st.info(f"Feature file {feature} will be created when you run this application.")

if __name__ == "__main__":
    main()