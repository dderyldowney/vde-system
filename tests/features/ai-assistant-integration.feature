Feature: AI Assistant Integration
  As a developer using VDE
  I want to use the AI assistant to manage my environment
  So I can control everything using natural language

  Scenario: Basic AI assistance
    Given I want help with VDE
    When I say "help me with VDE"
    Then the AI should explain available commands
    And I should understand what I can do

  Scenario: AI understands complex requests
    Given I need a complete development stack
    When I tell the AI "I need a Python backend with PostgreSQL database and Redis cache"
    Then the AI should understand all components
    And create Python, PostgreSQL, and Redis VMs
    And configure them to work together

  Scenario: AI provides context-aware help
    Given I have certain VMs running
    When I ask "what do I have running?"
    Then the AI should show my current state
    And suggest relevant next actions
    And provide helpful information

  Scenario: AI handles ambiguous requests
    Given my request is not clear
    When I say "start my environment"
    Then the AI should ask for clarification
    And the AI should make a reasonable guess based on context
    And the AI should explain what it's doing

  Scenario: AI remembers context
    Given I just created a Python VM
    When I say "start it"
    Then the AI should know "it" means Python
    And start the Python VM

  Scenario: AI suggests optimizations
    Given I'm doing something inefficient
    When I ask for advice
    Then the AI should suggest better approaches
    And explain why they're better
    And offer to implement them

  Scenario: AI handles errors gracefully
    Given something goes wrong
    When I ask the AI to fix it
    Then the AI should diagnose the problem
    And suggest solutions
    And offer to implement the fix

  Scenario: AI provides progress feedback
    Given I start a long operation
    When the AI is executing it
    Then I should see progress updates
    And know what's happening
    And understand how long it will take

  Scenario: AI learns preferences
    Given I use VDE regularly
    When I perform common actions
    Then the AI should learn my patterns
    And suggest shortcuts
    And anticipate my needs

  Scenario: AI explains technical details
    Given I don't understand something
    When I ask "how does this work?"
    Then the AI should explain clearly
    And provide examples
    And offer more details if needed

  Scenario: AI handles multiple operations
    Given I need to do several things
    When I say "create Python, start postgres, and show me how to connect"
    Then the AI should execute all operations
    And report on each one
    And confirm everything is complete

  Scenario: AI provides safety warnings
    Given I'm about to do something risky
    When the AI detects the risk
    Then it should warn me
    And explain the danger
    And ask for confirmation

  Scenario: AI offers alternatives
    Given I request something that might not be optimal
    When the AI has a better suggestion
    Then it should propose the alternative
    And explain the benefits
    And let me choose

  Scenario: AI works with dry-run mode
    Given I want to see what will happen
    When I enable dry-run mode
    Then the AI should explain what it would do
    And not actually do it
    And let me confirm before executing
