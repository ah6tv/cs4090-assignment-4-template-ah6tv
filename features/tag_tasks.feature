Feature: Tag Tasks
  As a user
  I want to add tags to my tasks
  So that I can organize and filter them better

  Scenario: Add tags to a task
    Given I have a basic task with title "Write documentation"
    When I add the tags "work,urgent,documentation" to the task
    Then the task should have the tags "work", "urgent", and "documentation"

  Scenario: Remove tag from a task
    Given I have a task with title "Project review" and tags "meeting,project,monthly"
    When I remove the tag "monthly" from the task
    Then the task should have the tags "meeting" and "project"
    And the task should not have the tag "monthly"

  Scenario: Filter tasks by tag
    Given I have the following tasks with tags:
      | title           | tags                 |
      | Write report    | work,report,writing  |
      | Team meeting    | work,meeting         |
      | Grocery shopping| personal,shopping    |
      | Finish proposal | work,report,proposal |
    When I filter tasks by tag "report"
    Then I should see 2 tasks in the filtered list
    And the filtered list should include "Write report"
    And the filtered list should include "Finish proposal"