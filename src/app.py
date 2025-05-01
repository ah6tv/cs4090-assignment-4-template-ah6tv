import streamlit as st
import pandas as pd
import subprocess
import json
import sys
from datetime import datetime
from tasks import (
    load_tasks, 
    save_tasks, 
    filter_tasks_by_priority, 
    filter_tasks_by_category, 
    generate_unique_id
)

def run_tests(test_file=None, extra_args=None):
    """
    Run pytest tests and return the results
    
    Args:
        test_file (str, optional): Specific test file to run
        extra_args (list, optional): Additional pytest arguments
        
    Returns:
        str: Test results as string
    """
    cmd = ["pytest", "-v"]
    
    if test_file:
        cmd.append(test_file)
    
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running tests: {str(e)}"

def run_coverage():
    """Run pytest with coverage reporting"""
    try:
        cmd = ["pytest", "--cov=tasks", "--cov-report", "term"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running coverage: {str(e)}"

def main():
    st.title("To-Do Application")
    
    # Add a tab structure
    tab1, tab2 = st.tabs(["Tasks", "Tests"])
    
    with tab1:
        # Load existing tasks
        tasks = load_tasks()
        
        # Sidebar for adding new tasks
        st.sidebar.header("Add New Task")
        
        # Task creation form
        with st.sidebar.form("new_task_form"):
            task_title = st.text_input("Task Title")
            task_description = st.text_area("Description")
            task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
            task_due_date = st.date_input("Due Date")
            submit_button = st.form_submit_button("Add Task")
        
        if submit_button and task_title:
            new_task = {
                "id": generate_unique_id(tasks),
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")
        
        # Main area to display tasks
        st.header("Your Tasks")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox("Filter by Category", ["All"] + list(set([task["category"] for task in tasks]) if tasks else []))
        with col2:
            filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
            show_completed = st.checkbox("Show Completed Tasks")
        
        # Apply filters
        filtered_tasks = tasks.copy()
        if filter_category != "All":
            filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
        if filter_priority != "All":
            filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
        if not show_completed:
            filtered_tasks = [task for task in filtered_tasks if not task.get("completed", False)]
        
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
                st.write(task["description"])
                st.caption(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")
            with col2:
                if st.button("Complete" if not task.get("completed", False) else "Undo", key=f"complete_{task['id']}"):
                    for t in tasks:
                        if t["id"] == task["id"]:
                            t["completed"] = not t.get("completed", False)
                            save_tasks(tasks)
                            st.rerun()
                if st.button("Delete", key=f"delete_{task['id']}"):
                    tasks = [t for t in tasks if t["id"] != task["id"]]
                    save_tasks(tasks)
                    st.rerun()
    
    with tab2:
        st.header("Test Suite")
        st.markdown("""
        This tab allows you to run automated tests for the To-Do List application.
        The tests verify that all core functionality is working correctly.
        """)
        
        st.subheader("Unit Tests")
        st.markdown("""
        Run basic unit tests to verify the functionality of individual functions in the `tasks.py` module.
        These tests validate that each function works correctly in isolation.
        """)
        
        if st.button("Run Unit Tests"):
            with st.spinner("Running unit tests..."):
                test_results = run_tests("test/test_basic.py")
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

if __name__ == "__main__":
    main()