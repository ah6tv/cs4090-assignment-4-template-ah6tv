Feature: Add Task
  As a user
  I want to add tasks to my to-do list
  So that I can keep track of what I need to do

  Scenario: Add a new task with basic information
    Given the to-do list is empty
    When I add a task with title "Buy groceries"
    Then the to-do list should contain 1 task
    And the task should have the title "Buy groceries"

  Scenario: Add a task with full details
    Given the to-do list is empty
    When I add a task with the following details:
      | title       | Buy new laptop      |
      | description | MacBook Pro 16-inch |
      | priority    | High               |
      | category    | Personal           |
      | due_date    | 2025-05-10         |
    Then the to-do list should contain 1 task
    And the task should have the title "Buy new laptop"
    And the task should have the priority "High"
    And the task should have the category "Personal"

  Scenario: Add multiple tasks
    Given the to-do list is empty
    When I add a task with title "Task 1"
    And I add a task with title "Task 2"
    And I add a task with title "Task 3"
    Then the to-do list should contain 3 tasks