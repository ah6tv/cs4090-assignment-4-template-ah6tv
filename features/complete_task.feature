Feature: Complete Task
  As a user
  I want to mark tasks as complete
  So that I can track my progress

  Scenario: Mark a task as complete
    Given I have a basic task with title "Write report"
    When I mark the task "Write report" as complete
    Then the task "Write report" should be marked as complete

  Scenario: Undo a completed task
    Given I have a task with title "Send email" that is completed
    When I mark the task "Send email" as incomplete
    Then the task "Send email" should be marked as incomplete

  Scenario: Filter completed tasks
    Given I have the following tasks:
      | title          | completed |
      | Finish project | true      |
      | Start design   | false     |
      | Call client    | true      |
    When I filter tasks by completion status "true"
    Then I should see 2 tasks in the filtered list
    And the filtered list should include "Finish project"
    And the filtered list should include "Call client"