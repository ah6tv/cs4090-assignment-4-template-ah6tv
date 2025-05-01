Feature: Recurring Tasks
  As a user
  I want to create recurring tasks
  So that I don't have to manually add repeating tasks

  Scenario: Create a daily recurring task
    Given the to-do list is empty
    When I add a recurring task with the following details:
      | title       | Daily standup       |
      | description | Team meeting        |
      | pattern     | daily               |
      | interval    | 1                   |
    Then the to-do list should contain 1 task
    And the task should be a recurring task
    And the task should have a recurrence pattern of "daily"
    And the task should have a recurrence interval of 1

  Scenario: Complete a recurring task and generate next occurrence
    Given I have a recurring task with title "Weekly report" and pattern "weekly"
    When I mark the task "Weekly report" as complete
    Then a new task "Weekly report" should be generated
    And the new task should have a due date 7 days after the original

  Scenario: List all recurring tasks
    Given I have the following tasks:
      | title           | recurrence_pattern | recurrence_interval |
      | Daily standup   | daily              | 1                   |
      | Weekly meeting  | weekly             | 1                   |
      | Monthly report  | monthly            | 1                   |
      | One-time task   |                    |                     |
    When I list all recurring tasks
    Then I should see 3 tasks in the list
    And the list should include "Daily standup"
    And the list should include "Weekly meeting"
    And the list should include "Monthly report"
    And the list should not include "One-time task"

  Scenario: Add a recurring task
    Given the to-do list is empty
    When I add a recurring task with the following details
     | title         | description       | priority | category | due_date   | pattern  | interval |
     | Water Plants  | Weekly reminder   | High     | Home     | 2025-05-01 | weekly   | 1        |
    Then the to-do list should contain 1 task(s)
    And the task should be a recurring task
    And the task should have a recurrence pattern of "weekly"
    And the task should have a recurrence interval of 1