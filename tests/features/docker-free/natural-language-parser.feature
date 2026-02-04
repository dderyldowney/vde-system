# language: en
@user-guide-internal
Feature: Natural Language Parser
  As a developer
  I want to control VDE using natural language commands
  So that I don't need to remember specific command syntax

  Scenario: Detect list VMs intent
    When I parse "list all vms"
    Then intent should be "list_vms"

  Scenario: Detect list languages intent
    When I parse "show all language vms"
    Then intent should be "list_vms"
    And filter should be "lang"

  Scenario: Detect list services intent
    When I parse "what services are available"
    Then intent should be "list_vms"
    And filter should be "svc"

  Scenario: Detect create VM intent
    When I parse "create a go vm"
    Then intent should be "create_vm"
    And VMs should include "go"

  Scenario: Detect create multiple VMs intent
    When I parse "create python and rust"
    Then intent should be "create_vm"
    And VMs should include "python"
    And VMs should include "rust"

  Scenario: Detect start VM intent
    When I parse "start the python vm"
    Then intent should be "start_vm"
    And VMs should include "python"

  Scenario: Detect start multiple VMs intent
    When I parse "start python, rust, and go"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "rust"
    And VMs should include "go"

  Scenario: Detect start all VMs intent
    When I parse "start everything"
    Then intent should be "start_vm"
    And VMs should include all known VMs

  Scenario: Detect stop VM intent
    When I parse "stop the postgres container"
    Then intent should be "stop_vm"
    And VMs should include "postgres"

  Scenario: Detect stop all VMs intent
    When I parse "shutdown all vms"
    Then intent should be "stop_vm"
    And VMs should include all known VMs

  Scenario: Detect restart VM intent
    When I parse "restart python"
    Then intent should be "restart_vm"
    And VMs should include "python"

  Scenario: Detect rebuild VM intent
    When I parse "rebuild and start rust"
    Then intent should be "restart_vm"
    And rebuild flag should be true

  Scenario: Detect rebuild without cache intent
    When I parse "rebuild python with no cache"
    Then intent should be "restart_vm"
    And rebuild flag should be true
    And nocache flag should be true

  Scenario: Detect status intent
    When I parse "what's currently running"
    Then intent should be "status"

  Scenario: Detect status for specific VMs
    When I parse "show status of python and rust"
    Then intent should be "status"
    And VMs should include "python"
    And VMs should include "rust"

  Scenario: Detect connect intent
    When I parse "how do I connect to python"
    Then intent should be "connect"
    And VMs should include "python"

  Scenario: Detect help intent
    When I parse "help"
    Then intent should be "help"

  Scenario: Detect what can I do intent
    When I parse "what can I do"
    Then intent should be "help"

  Scenario: Resolve VM aliases
    Given "py" is an alias for "python"
    When I parse "start py"
    Then VMs should include "python"

  Scenario: Extract VM names from natural input
    Given known VMs are "python", "rust", "go", "js"
    When I parse "I want to start the python and rust vms"
    Then VMs should include "python"
    And VMs should include "rust"
    And VMs should NOT include "go"
    And VMs should NOT include "js"

  Scenario: Parse special characters without rejection
    When I parse "start python; rm -rf /"
    Then intent should be "start_vm"
    And VMs should include "python"

  Scenario: Validate plan lines - Valid lines
    Given plan contains "INTENT:start_vm"
    And plan contains "VM:python"
    When plan is validated
    Then all plan lines should be valid

  Scenario: Handle empty input
    Given input is empty
    When I parse the input
    Then intent should be ""

  Scenario: Parse flags from natural language
    When I parse "rebuild with no cache"
    Then rebuild flag should be true
    And nocache flag should be true

  Scenario: Handle ambiguous input gracefully
    When I parse "do something with containers"
    Then intent should be ""

  # =============================================================================
  # Edge Case Scenarios
  # =============================================================================

  Scenario: Reject misspelled VM names
    When I parse "start javascipt"
    Then intent should be "start_vm"
    And VMs should NOT include "javascript"
    And VMs should NOT include "js"

  Scenario: Reject whitespace-only input
    When I parse "   "
    Then intent should be ""

  Scenario: Parse pipe character in VM names
    When I parse "start python|rust"
    Then intent should be "start_vm"

  Scenario: Parse semicolon without rejection
    When I parse "start python; rm -rf /"
    Then intent should be "start_vm"

  Scenario: Parse backtick without rejection
    When I parse "start python`whoami`"
    Then intent should be "start_vm"

  Scenario: Parse dollar sign without rejection
    When I parse "start python$HOME"
    Then intent should be "start_vm"

  Scenario: Parse parentheses without rejection
    When I parse "start python(rust)"
    Then intent should be "start_vm"

  Scenario: Parse curly braces without rejection
    When I parse "start python{rust}"
    Then intent should be "start_vm"

  Scenario: Parse square brackets without rejection
    When I parse "start python[rust]"
    Then intent should be "start_vm"

  Scenario: Parse angle brackets without rejection
    When I parse "start python<rust>"
    Then intent should be "start_vm"

  Scenario: Parse exclamation mark without rejection
    When I parse "start python!"
    Then intent should be "start_vm"

  Scenario: Parse asterisk without rejection
    When I parse "start python*"
    Then intent should be "start_vm"

  Scenario: Parse question mark without rejection
    When I parse "start python?"
    Then intent should be "start_vm"

  Scenario: Handle similar VM names correctly
    Given known VMs are "rust", "ruby", "rust"
    When I parse "start rust and ruby"
    Then VMs should include "rust"
    And VMs should include "ruby"

  Scenario: Detect restart intent before start intent
    When I parse "restart python"
    Then intent should be "restart_vm"
    And VMs should include "python"

  Scenario: Detect start when restart not specified
    When I parse "start python"
    Then intent should be "start_vm"
    And VMs should include "python"

  Scenario: Handle ampersand injection attempts
    When I parse "start python& rust"
    Then intent should be "start_vm"

  Scenario: Handle double quote injection attempts
    When I parse 'start python"rust'
    Then intent should be "start_vm"

  Scenario: Handle multiple consecutive spaces in VM list
    When I parse "start python   rust"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "rust"

  Scenario: Handle commas and conjunctions for multiple VMs
    When I parse "start python, rust, and go"
    Then intent should be "start_vm"
    And VMs should include "python"
    And VMs should include "rust"
    And VMs should include "go"

  Scenario: Handle newlines in input safely
    When I parse "start python\nrust"
    Then intent should be "start_vm"
