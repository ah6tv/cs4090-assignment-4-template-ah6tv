Feature: Filter Tasks
  As a user
  I want to filter tasks by different criteria
  So that I can find relevant tasks quickly

  Scenario: Filter tasks by priority
    Given I have the following tasks:
      | title           | priority |
      | Urgent meeting  | High     |
      | Review document | Medium   |
      | Weekly report   | High     |
      | Clean desk      | Low      |
    When I filter tasks by priority "High"
    Then I should see 2 tasks in the filtered list
    And the filtered list should include "Urgent meeting"
    And the filtered list should include "Weekly report"

  Scenario: Filter tasks by category
    Given I have the following tasks:
      | title           | category  |
      | Team meeting    | Work      |
      | Dentist         | Personal  |
      | Update resume   | Work      |
      | Call mom        | Personal  |
      | Gym session     | Health    |
    When I filter tasks by category "Personal"
    Then I should see 2 tasks in the filtered list
    And the filtered list should include "Dentist"
    And the filtered list should include "Call mom"

  Scenario: Search tasks by keyword
    Given I have the following tasks:
      | title              | description           |
      | Buy groceries      | Get milk and bread    |
      | Prepare presentation| For the sales meeting |
      | Milk the cow       | Farm work             |
    When I search for tasks containing "milk"
    Then I should see 2 tasks in the filtered list
    And the filtered list should include "Buy groceries"
    And the filtered list should include "Milk the cow"